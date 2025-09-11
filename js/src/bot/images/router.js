import { Router } from 'aiogram';
import { types, InlineKeyboardMarkup, InlineKeyboardButton } from 'aiogram/types.js';

import { TextCommand, StateCommand } from '../filters.js';
import { isEmptyPrompt } from '../empty_prompt.js';
import { imagesCommand, imagesCommandText } from '../commands.js';
import { createMainKeyboard } from '../main_keyboard.js';
import { sendPhotoAsFile } from '../utils.js';
import { DEFAULT_ERROR_MESSAGE } from '../constants.js';
import { stateService, StateTypes } from '../../services/state_service.js';
import { imageService } from '../../services/image_service.js';
import { tokenizeService } from '../../services/tokenize_service.js';
import { imageModelsValues, samplersValues, sizeValues, stepsValues, cgfValues } from '../../services/image_utils.js';

export const imagesRouter = new Router();

// Confirmed banned words
const confirmedBannedWords = [
  'blood','chest','cutting','dick','flesh','miniskirt','naked','nude','provocative','sex','sexy','shirtless','shit','succubus','trump'
];

// Unconfirmed banned words
const unconfirmedBannedWords = {
  gore_words: [
    "blood","bloodbath","crucifixion","bloody","flesh","bruises","car crash","corpse",
    "crucified","cutting","decapitate","infested","gruesome","kill","infected","sadist",
    "slaughter","teratoma","tryphophobia","wound","cronenberg","khorne","cannibal",
    "cannibalism","visceral","guts","bloodshot","gory","killing","surgery","vivisection",
    "massacre","hemoglobin","suicide"
  ],
  adult_words: [
    "ahegao","pinup","ballgag","playboy","bimbo","pleasure","bodily fluids","pleasures",
    "boudoir","rule34","brothel","seducing","dominatrix","seductive","erotic seductive",
    "fuck","sensual","hardcore","sexy","hentai","shag","horny","shibari","incest",
    "smut","jav","succubus","jerk off king at pic","thot","kinbaku","transparent",
    "submissive","dominant","nasty","indecent","legs spread","cussing","flashy","twerk",
    "making love","voluptuous","naughty","wincest","orgy","sultry","xxx","bondage",
    "bdsm","dog collar","slavegirl","transparent and translucent"
  ],
  body_parts_words: [
    "arse","labia","ass","mammaries","human centipede","badonkers","minge","massive chests",
    "big ass","mommy milker","booba","nipple","booty","oppai","bosom","melons","bulging",
    "coochie","head","engorged","organs","breasts","ovaries","busty","penis","clunge",
    "phallus","crotch","sexy female","dick","skimpy","girth","thick","honkers","vagina",
    "hooters","veiny","knob","seductress","shaft"
  ],
  nudity_words: [
    "no clothes","speedo","au naturale","no shirt","bare chest","nude","barely dressed",
    "bra","risqué","clear","scantily","clad","cleavage","stripped","full frontal unclothed",
    "invisible clothes","wearing nothing","lingerie with no shirt","naked","without clothes on",
    "negligee","zero clothes"
  ],
  taboo_words: [
    "taboo","fascist","nazi","prophet mohammed","slave","coon","honkey","arrested","jail",
    "handcuffs","torture","disturbing","1488"
  ],
  drugs_words: [
    "drugs","cocaine","heroin","meth","crack"
  ],
  other_words: [
    "farts","fart","poop","warts","xi jinping","shit","pleasure","errect","big black",
    "brown pudding","bunghole","vomit","voluptuous","seductive","sperm","hot","sexy",
    "plebeian","sensored","censored","uncouth","silenced","deepfake","inappropriate",
    "pus","waifu","mp5","succubus","surgery"
  ]
};

// Build banned words set
const bannedWordsSet = new Set(confirmedBannedWords);
Object.values(unconfirmedBannedWords).flat().forEach(w => bannedWordsSet.add(w));

function isBannedWord(word) {
  return bannedWordsSet.has(word.toLowerCase());
}

function getBannedWords(text) {
  return text.split(' ').map(w => w.toLowerCase()).filter(isBannedWord);
}

// Handle Stable Diffusion generation when in Image state
imagesRouter.message(StateCommand(StateTypes.Image), async (message) => {
  const userId = message.from_user.id;

  if (!(await stateService.isImageState(userId))) return;

  try {
    const tokens = await tokenizeService.get_tokens(userId);
    if (tokens.tokens < 0) {
      await message.answer(ctx.t('errors.not_enough_energy'));
      await stateService.setCurrentState(userId, StateTypes.Default);
      return;
    }

    if (isEmptyPrompt(message.text)) {
      await message.answer(
        '🚫 В вашем запросе отсутствует описание изображения 🖼️. Пожалуйста, попробуйте снова.',
        { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
          new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-sd-generate' })
        ]] }) }
      );
      return;
    }

    await stateService.setCurrentState(userId, StateTypes.Default);
    const waitMsg = await message.answer('**⌛️Ожидайте генерацию...**\nПримерное время ожидания 15-30 секунд.');

    await message.bot.sendChatAction(message.chat.id, 'typing');
    imageService.setWaitingImage(userId, true);

    async function waitImage() {
      await message.answer('Генерация изображения ушла в фоновый режим. \nПришлем вам изображение через 40-120 секунд. \nМожете продолжать работать с ботом 😉');
    }

    const result = await imageService.generate(message.text, userId, waitImage);
    await message.bot.sendChatAction(message.chat.id, 'typing');
    await message.replyPhoto(result.output[0]);
    await sendPhotoAsFile(message, result.output[0], 'Вот картинка в оригинальном качестве');
    await tokenizeService.update_user_token(userId, 30, 'subtract');
    await message.answer(`🤖 Затрачено на генерацию изображения Stable Diffusion 30⚡️\n\n❔ /help - Информация по ⚡️`);
    await waitMsg.delete();

  } catch (e) {
    console.error(e);
    await message.answer(DEFAULT_ERROR_MESSAGE);
  }

  imageService.setWaitingImage(userId, false);
  await stateService.setCurrentState(userId, StateTypes.Default);
});

// Handle Flux generation when in Flux state
imagesRouter.message(StateCommand(StateTypes.Flux), async (message) => {
  const userId = message.from_user.id;
  if (!(await stateService.isFluxState(userId))) return;
  try {
    const tokens = await tokenizeService.get_tokens(userId);
    if (tokens.tokens < 0) {
      await message.answer(ctx.t('errors.not_enough_energy'));
      await stateService.setCurrentState(userId, StateTypes.Default);
      return;
    }
    if (isEmptyPrompt(message.text)) {
      await message.answer(
        '🚫 В вашем запросе отсутствует описание изображения 🖼️. Пожалуйста, попробуйте снова.',
        { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
          new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-flux-generate' })
        ]] }) }
      );
      return;
    }
    await stateService.setCurrentState(userId, StateTypes.Default);
    const waitMsg = await message.answer('**⌛️Ожидайте генерацию...**\nПримерное время ожидания 15-30 секунд.');
    await message.bot.sendChatAction(message.chat.id, 'typing');
    imageService.setWaitingImage(userId, true);
    async function taskIdGet(taskId) {
      await message.answer(`\`1:flux:${taskId}:generate\``);
      await message.answer(`Это ID вашей генерации.\n\nПросто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.\n\nВы также получите результат генерации по готовности.`);
    }
    const result = await imageService.generateFlux(userId, message.text, taskIdGet);
    const imageUrl = result.data.output.image_url;
    await message.bot.sendChatAction(message.chat.id, 'typing');
    await message.replyPhoto(imageUrl);
    await sendPhotoAsFile(message, imageUrl, 'Вот картинка в оригинальном качестве');
    await message.answer('Cгенерировать Flux еще? 🔥', { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
      new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'flux-generate' })
    ]] }) });
    const model = await imageService.getFluxModel(userId);
    let energy = model === 'Qubico/flux1-dev' ? 2000 : 600;
    await tokenizeService.update_user_token(userId, energy, 'subtract');
    await message.answer(`🤖 Затрачено на генерацию изображения Flux ${energy}⚡️ \n\n❔ /help - Информация по ⚡️`);
    await waitMsg.delete();
  } catch (e) {
    console.error('Failed to generate Flux image:', e);
    await message.answer(DEFAULT_ERROR_MESSAGE);
  }
  imageService.setWaitingImage(userId, false);
  await stateService.setCurrentState(userId, StateTypes.Default);
});

// Handle DALL·E 3 generation when in Dalle3 state
imagesRouter.message(StateCommand(StateTypes.Dalle3), async (message) => {
  const userId = message.from_user.id;
  if (!(await stateService.isDalle3State(userId))) return;
  try {
    const tokens = await tokenizeService.get_tokens(userId);
    if (tokens.tokens < 0) {
      await message.answer(ctx.t('errors.not_enough_energy'));
      await stateService.setCurrentState(userId, StateTypes.Default);
      return;
    }
    if (isEmptyPrompt(message.text)) {
      await message.answer(
        '🚫 В вашем запросе отсутствует описание изображения 🖼️. Пожалуйста, попробуйте снова.',
        { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
          new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-dalle-generate' })
        ]] }) }
      );
      return;
    }
    await stateService.setCurrentState(userId, StateTypes.Default);
    const waitMsg = await message.answer('**⌛️Ожидайте генерацию...**\nПримерное время ожидания 15-30 секунд.');
    await message.bot.sendChatAction(message.chat.id, 'typing');
    imageService.setWaitingImage(userId, true);
    const imgResult = await imageService.generateDALLE(userId, message.text);
    await message.bot.sendChatAction(message.chat.id, 'typing');
    await message.answer(imgResult.text);
    await message.replyPhoto(imgResult.image);
    await sendPhotoAsFile(message, imgResult.image, 'Вот картинка в оригинальном качестве');
    await message.answer('Cгенерировать DALL·E 3 еще? 🔥', { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
      new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'dalle-generate' })
    ]] }) });
    await waitMsg.delete();
    await tokenizeService.update_user_token(userId, imgResult.total_tokens * 2, 'subtract');
    await message.answer(`🤖 Затрачено на генерацию изображения DALL·E 3 **${imgResult.total_tokens * 2}**⚡️\n\n❔ /help - Информация по ⚡️`);
  } catch (e) {
    console.error('Failed to generate DALL·E 3 image:', e);
    await message.answer(DEFAULT_ERROR_MESSAGE);
    await stateService.setCurrentState(userId, StateTypes.Default);
  }
});

// Helper to show Upscale/Variation options for Midjourney results
async function sendVariationImage(message, imageUrl, taskId) {
  const markup = new InlineKeyboardMarkup({ inline_keyboard: [
    [
      new InlineKeyboardButton({ text: 'U1', callback_data: `upscale-midjourney ${taskId} 1` }),
      new InlineKeyboardButton({ text: 'U2', callback_data: `upscale-midjourney ${taskId} 2` }),
      new InlineKeyboardButton({ text: 'V1', callback_data: `variation-midjourney ${taskId} 1` }),
      new InlineKeyboardButton({ text: 'V2', callback_data: `variation-midjourney ${taskId} 2` })
    ]
  ]});
  const caption = `Номера вариаций:
+-------+-------+
|   1   |   2   |
+-------+-------+
|   3   |   4   |
+-------+-------+

Доступные действия:
U - Увеличить изображение (Upscale)
V - Сгенерировать вариации выбранного изображения (Variation)

Ваш task ID: ${taskId}
Выберите действие:`;
  await sendPhotoAsFile(message, imageUrl, caption, '.png', markup);
}

// Handle Midjourney generation when in Midjourney state
imagesRouter.message(StateCommand(StateTypes.Midjourney), async (message) => {
  const userId = message.from_user.id;
  if (!(await stateService.isMidjourneyState(userId))) return;
  try {
    const tokens = await tokenizeService.get_tokens(userId);
    if (tokens.tokens < 0) {
      await message.answer(ctx.t('errors.not_enough_energy'));
      await stateService.setCurrentState(userId, StateTypes.Default);
      return;
    }
    await message.bot.sendChatAction(message.chat.id, 'typing');
    async function taskIdGet(taskId) {
      await message.answer(`\`1:midjourney:${taskId}:generate\``);
    }
    const result = await imageService.generateMidjourney(userId, message.text, taskIdGet);
    if (result.status === 'finished') {
      const imageUrl = result.task_result.discord_image_url;
      await sendVariationImage(message, imageUrl, result.task_id);
      return;
    }
    if (result.status === 'processing') {
      await message.answer('⌛️ Задача в процессе!');
      return;
    }
    await message.answer(DEFAULT_ERROR_MESSAGE);
  } catch (e) {
    console.error('Failed to generate Midjourney task:', e);
    await message.answer(DEFAULT_ERROR_MESSAGE);
  }
  await stateService.setCurrentState(userId, StateTypes.Default);
});

// Handle upscale callbacks for Midjourney images
imagesRouter.callbackQuery(StartWithQuery('upscale-midjourney'), async (callbackQuery) => {
  const [_, taskId, index] = callbackQuery.data.split(' ');
  await callbackQuery.answer();
  async function taskIdGet(newTaskId) {
    await callbackQuery.message.answer(`\`1:midjourney:${newTaskId}:generate\``);
  }
  const result = await imageService.upscaleImage(taskId, parseInt(index, 10), taskIdGet);
  if (result.status === 'finished') {
    await sendVariationImage(callbackQuery.message, result.task_result.discord_image_url, result.task_id);
  } else if (result.status === 'processing') {
    await callbackQuery.message.answer('⌛️ Задача в процессе!');
  } else {
    await callbackQuery.message.answer(DEFAULT_ERROR_MESSAGE);
  }
});

// Handle variation callbacks for Midjourney images
imagesRouter.callbackQuery(StartWithQuery('variation-midjourney'), async (callbackQuery) => {
  const [_, taskId, index] = callbackQuery.data.split(' ');
  await callbackQuery.answer();
  const waitMsg = await callbackQuery.message.answer('**⌛️Ожидайте генерацию...**\nПримерное время ожидания **1-3 минуты**.');
  async function taskIdGet(newTaskId) {
    await callbackQuery.message.answer(`\`1:midjourney:${newTaskId}:generate\``);
    await callbackQuery.message.answer(`Это ID вашей генерации.\n\nПросто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.\n\nВы также получите результат генерации по готовности.`);
  }
  const result = await imageService.variationImage(taskId, parseInt(index, 10), taskIdGet);
  await sendVariationImage(callbackQuery.message, result.task_result.discord_image_url, result.task_id);
  await tokenizeService.update_user_token(callbackQuery.from_user.id, 8700, 'subtract');
  await callbackQuery.message.answer(`\n🤖 Затрачено на генерацию вариации изображения Midjourney 8700⚡️\n\n❔ /help - Информация по ⚡️`);
  await waitMsg.delete();
});

// Handle /image command entrypoint
imagesRouter.message(TextCommand([imagesCommand, imagesCommandText]), async (message) => {
  await message.answer(`🖼️ Выберите модель:

⦁ [Midjourney](https://en.wikipedia.org/wiki/Midjourney)
⦁ [DALL·E 3](https://en.wikipedia.org/wiki/DALL-E)
⦁ [Flux](https://en.wikipedia.org/wiki/FLUX.1)
⦁ [Stable Diffusion](https://en.wikipedia.org/wiki/Stable_Diffusion)
`, {
    reply_markup: new InlineKeyboardMarkup({
      resize_keyboard: true,
      inline_keyboard: [
        [
          new InlineKeyboardButton({ text: 'Midjourney', callback_data: 'image-model Midjourney' }),
          new InlineKeyboardButton({ text: 'DALL·E 3', callback_data: 'image-model Dalle3' })
        ],
        [
          new InlineKeyboardButton({ text: 'Flux', callback_data: 'image-model Flux' }),
          new InlineKeyboardButton({ text: 'Stable Diffusion', callback_data: 'image-model SD' })
        ]
      ]
    })
  });
  await message.bot.sendChatAction(message.chat.id, 'typing');
});

// Generate base Stable Diffusion keyboard
async function generateBaseStableDiffusionKeyboard(callbackQuery) {
  const userId = callbackQuery.from_user.id;
  const currentImage = await imageService.getCurrentImage(userId);
  const currentSize = await imageService.getSizeModel(userId);
  const currentSteps = await imageService.getSteps(userId);
  const currentCfg = await imageService.getCfgModel(userId);
  await callbackQuery.message.editText('Параметры **Stable Diffusion**:', { parse_mode: 'MarkdownV2' });
  await callbackQuery.message.editReplyMarkup({ reply_markup: new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [
      [new InlineKeyboardButton({ text: `Модель: ${currentImage}`, callback_data: 'image-model choose-model 0 5' })],
      [new InlineKeyboardButton({ text: `Размер: ${currentSize}`, callback_data: 'image-model choose-size 0 5' })],
      [
        new InlineKeyboardButton({ text: `Шаги: ${currentSteps}`, callback_data: 'image-model choose-steps' }),
        new InlineKeyboardButton({ text: `CFG Scale: ${currentCfg}`, callback_data: 'image-model choose-cfg' })
      ],
      [new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'sd-generate' })]
    ]
  }) });
}

// Generate base Midjourney keyboard
async function generateBaseMidjourneyKeyboard(callbackQuery) {
  const userId = callbackQuery.from_user.id;
  const currentSize = await imageService.getMidjourneySize(userId);
  const sizeText = (size) => currentSize === size ? `✅ ${size}` : size;
  await callbackQuery.message.editText(`Параметры **Midjourney**:

Выберите соотношение сторон изображения. Текущее соотношение отмечено галочкой.

После этого нажмите кнопку \`Сгенерировать\`.`, { parse_mode: 'MarkdownV2' });
  await callbackQuery.message.editReplyMarkup({ reply_markup: new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [
      [
        new InlineKeyboardButton({ text: sizeText('1:1'), callback_data: 'image-model update-size-midjourney 1:1' }),
        new InlineKeyboardButton({ text: sizeText('2:3'), callback_data: 'image-model update-size-midjourney 2:3' }),
        new InlineKeyboardButton({ text: sizeText('3:2'), callback_data: 'image-model update-size-midjourney 3:2' })
      ],
      [
        new InlineKeyboardButton({ text: sizeText('4:5'), callback_data: 'image-model update-size-midjourney 4:5' }),
        new InlineKeyboardButton({ text: sizeText('5:4'), callback_data: 'image-model update-size-midjourney 5:4' }),
        new InlineKeyboardButton({ text: sizeText('4:7'), callback_data: 'image-model update-size-midjourney 4:7' }),
        new InlineKeyboardButton({ text: sizeText('7:4'), callback_data: 'image-model update-size-midjourney 7:4' })
      ],
      [
        new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'midjourney-generate' }),
        new InlineKeyboardButton({ text: '❌ Отменить', callback_data: 'cancel-midjourney-generate' })
      ]
    ]
  }) });
}

// Generate base DALL·E 3 keyboard
async function generateBaseDalle3Keyboard(callbackQuery) {
  const userId = callbackQuery.from_user.id;
  const currentSize = await imageService.getDALLESize(userId);
  const sizeText = (size) => currentSize === size ? `✅ ${size}` : size;
  await callbackQuery.message.editText('Параметры **Dall-e-3**:', { parse_mode: 'MarkdownV2' });
  await callbackQuery.message.editReplyMarkup({ reply_markup: new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [
      [new InlineKeyboardButton({ text: sizeText('1024x1024'), callback_data: 'image-model update-size-dalle 1024x1024' })],
      [new InlineKeyboardButton({ text: sizeText('1024x1792'), callback_data: 'image-model update-size-dalle 1024x1792' })],
      [new InlineKeyboardButton({ text: sizeText('1792x1024'), callback_data: 'image-model update-size-dalle 1792x1024' })],
      [new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'dalle-generate' })]
    ]
  }) });
}

// Generate base Flux keyboard
async function generateBaseFluxKeyboard(callbackQuery) {
  const userId = callbackQuery.from_user.id;
  const currentModel = await imageService.getFluxModel(userId);
  const modelText = (model, text) => currentModel === model ? `✅ ${text}` : text;
  await callbackQuery.message.editText('Параметры **Flux**:', { parse_mode: 'MarkdownV2' });
  await callbackQuery.message.editReplyMarkup({ reply_markup: new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [
      [new InlineKeyboardButton({ text: modelText('Qubico/flux1-dev', 'Модель: Flux-Dev'), callback_data: 'image-model update-flux-model Qubico/flux1-dev' })],
      [new InlineKeyboardButton({ text: modelText('Qubico/flux1-schnell', 'Модель: Flux-Schnell'), callback_data: 'image-model update-flux-model Qubico/flux1-schnell' })],
      [new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'flux-generate' })]
    ]
  }) });
}

// Handle Stable Diffusion generate request
imagesRouter.callbackQuery(StartWithQuery('sd-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Image);
  await callbackQuery.message.answer(
    `Напишите запрос для генерации изображения! 🖼️

Например: \`an astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed\``,
    {
      reply_markup: new InlineKeyboardMarkup({
        resize_keyboard: true,
        inline_keyboard: [
          [new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-sd-generate' })]
        ]
      })
    }
  );
});

// Handle cancellation of Stable Diffusion generate mode
imagesRouter.callbackQuery(StartWithQuery('cancel-sd-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Default);
  await callbackQuery.message.delete();
  await callbackQuery.answer('Режим генерации изображения в Stable Diffusion успешно отменён!');
});

// Handle Flux generate request
imagesRouter.callbackQuery(StartWithQuery('flux-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Flux);
  await callbackQuery.message.answer(
    `Напишите запрос для генерации изображения! 🖼️

Например: \`an astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed\``,
    {
      reply_markup: new InlineKeyboardMarkup({
        resize_keyboard: true,
        inline_keyboard: [
          [new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-flux-generate' })]
        ]
      })
    }
  );
});

// Handle cancellation of Flux generate mode
imagesRouter.callbackQuery(StartWithQuery('cancel-flux-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Default);
  await callbackQuery.message.delete();
  await callbackQuery.answer('Режим генерации изображения в Flux успешно отменён!');
});

// Handle DALL·E 3 generate request
imagesRouter.callbackQuery(StartWithQuery('dalle-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Dalle3);
  await callbackQuery.message.answer(
    `Напишите запрос для генерации изображения! 🖼️

Например: \`Нарисуй черную дыру, которая поглощает галактики\``,
    {
      reply_markup: new InlineKeyboardMarkup({
        resize_keyboard: true,
        inline_keyboard: [
          [new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-dalle-generate' })]
        ]
      })
    }
  );
});

// Handle cancellation of DALL·E 3 generate mode
imagesRouter.callbackQuery(StartWithQuery('cancel-dalle-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Default);
  await callbackQuery.message.delete();
  await callbackQuery.answer('Режим генерации изображения в DALL·E 3 отменен.');
});

// Handle Midjourney generate request
imagesRouter.callbackQuery(StartWithQuery('midjourney-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Midjourney);
  await callbackQuery.message.delete();
  await callbackQuery.message.answer(
    'Выберите один из вариантов запроса для генерации изображения 🖼️ в меню снизу.',
    { reply_markup: new types.ReplyKeyboardMarkup({ keyboard: [
        [new types.KeyboardButton({ text: 'Photorealistic black hole in space, absorbing galaxies.' })],
        [new types.KeyboardButton({ text: 'Силуэт города ночью, футуристический, неоновые огни, высокая детализация.' })],
        [new types.KeyboardButton({ text: 'An astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed.' })]
      ], resize_keyboard: true, one_time_keyboard: true }) }
  );
  await callbackQuery.message.answer(
    'Или напишите свой запрос для генерации изображения на любом языке, выбор языка может менять стилистические особенности изображений.\n\nНапример: "город" на русском языке может выглядеть как город из России, а "city" на английском языке как город из США или из другой страны.',
    { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
        new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-midjourney-generate' })
      ]], resize_keyboard: true }) }
  );
});

// Handle cancellation of Midjourney generate mode
imagesRouter.callbackQuery(StartWithQuery('cancel-midjourney-generate'), async (callbackQuery) => {
  await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Default);
  await callbackQuery.message.delete();
  const mainKeyboard = createMainKeyboard();
  await callbackQuery.message.answer('Режим генерации изображения в Midjourney успешно отменён!', { reply_markup: mainKeyboard });
});

// Handle image model selection and settings
imagesRouter.callbackQuery(StartWithQuery('image-model'), async (callbackQuery) => {
  const parts = callbackQuery.data.split(' ');
  const model = parts[1];
  const userId = callbackQuery.from_user.id;
  if (model === 'SD') return await generateBaseStableDiffusionKeyboard(callbackQuery);
  if (model === 'Dalle3') return await generateBaseDalle3Keyboard(callbackQuery);
  if (model === 'Midjourney') return await generateBaseMidjourneyKeyboard(callbackQuery);
  if (model === 'Flux') return await generateBaseFluxKeyboard(callbackQuery);
  if (model === 'update-flux-model') {
    const value = parts[2]; await imageService.setFluxModel(userId, value); return await generateBaseFluxKeyboard(callbackQuery);
  }
  if (model === 'update-size-midjourney') {
    const size = parts[2]; await imageService.setMidjourneySize(userId, size); return await generateBaseMidjourneyKeyboard(callbackQuery);
  }
  if (model === 'update-size-dalle') {
    const size = parts[2]; await imageService.setDALLESize(userId, size); return await generateBaseDalle3Keyboard(callbackQuery);
  }
  if (model === 'update-model') {
    const newModel = parts[2]; await imageService.setCurrentImage(userId, newModel); return await generateBaseStableDiffusionKeyboard(callbackQuery);
  }
  if (model === 'update-sampler') {
    const sampler = parts[2]; await imageService.setSamplerState(userId, sampler); return await generateBaseStableDiffusionKeyboard(callbackQuery);
  }
  // TODO: implement choose-model, choose-size, choose-sampler, choose-steps, choose-cfg handlers
});
