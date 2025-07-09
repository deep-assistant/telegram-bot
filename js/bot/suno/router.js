import { Router } from 'aiogram';
import { InlineKeyboardButton, InlineKeyboardMarkup } from 'aiogram/types.js';
import { TextCommand, StateCommand, StartWithQuery } from '../filters.js';
import { SUNO_COMMAND, SUNO_TEXT } from '../commands.js';
import { isEmptyPrompt } from '../empty_prompt.js';
import { DEFAULT_ERROR_MESSAGE } from '../constants.js';
import { stateService, StateTypes, sunoService, tokenizeService } from '../../services/index.js';

export const sunoRouter = new Router();

// Render generated Suno clip messages
async function sunoCreateMessages(message, generation) {
  const clip = Object.values(generation.data.output.clips)[0];
  // send image
  await message.answerPhoto(clip.image_large_url, { caption: `Текст *«${clip.title}»*\n\n${clip.metadata.prompt}` });
  // send audio and video
  await message.answerDocument(clip.audio_url);
  await message.answerVideo(clip.video_url);
  // prompt to generate again
  await message.answer('Cгенерировать Suno еще? 🔥', {
    reply_markup: new InlineKeyboardMarkup({
      resize_keyboard: true,
      inline_keyboard: [[
        new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'suno-generate' })
      ]]
    })
  });
}

export { sunoCreateMessages };

// Handle Suno task fetch state
sunoRouter.message(
  StateCommand(StateTypes.Suno),
  async (message) => {
    const userId = message.from_user.id;
    if (!(await stateService.isSunoState(userId))) return;
    try {
      const tokens = await tokenizeService.get_tokens(userId);
      if (tokens.tokens < 0) {
        await message.answer(`У вас не хватает *⚡️*. 😔\n\n/balance - ✨ Проверить Баланс\n/buy - 💎 Пополнить баланс\n/referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!`);
        await stateService.setCurrentState(userId, StateTypes.Default);
        return;
      }
      if (isEmptyPrompt(message.text)) {
        await message.answer(
          '🚫 В вашем запросе отсутствует описание музыкальной композиции 🎵. Пожалуйста, попробуйте снова.',
          { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
            new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-suno-generate' })
          ]] }) }
        );
        return;
      }
      if (message.text.length > 200) {
        await message.answer(
          'Описание музыкальной композиции 🎵 *не может быть более 200 символов* для Suno.\n\nПожалуйста, попробуйте промт короче.',
          { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
            new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-suno-generate' })
          ]] }) }
        );
        return;
      }
      await stateService.setCurrentState(userId, StateTypes.Default);
      const waitMessage = await message.answer(`**⌛️Ожидайте генерацию...**\nПримерное время ожидания: *3-5 минут*.\nМожете продолжать работать с ботом`);
      await message.bot.sendChatAction(message.chat.id, 'typing');
      async function taskIdGet(taskId) {
        await message.answer(`\`1:suno:${taskId}:generate\``);
        await message.answer('Это ID вашей генерации.\n\nПросто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.\n\nВы также получите результат генерации по готовности.');
      }
      const generation = await sunoService.generateSuno(message.text, taskIdGet);
      await sunoCreateMessages(message, generation);
      await tokenizeService.update_user_token(userId, 5700, 'subtract');
      await message.answer(`\n🤖 Затрачено на генерацию музыкальной композиции *Suno*: *5700*\n\n❔ /help - Информация по ⚡️`);
      await waitMessage.delete();
    } catch (e) {
      console.error('Failed to generate Suno:', e);
      await message.answer(DEFAULT_ERROR_MESSAGE);
      await stateService.setCurrentState(userId, StateTypes.Default);
    }
  }
);

// Prepare Suno state on /suno or button
sunoRouter.message(
  TextCommand([SUNO_COMMAND, SUNO_TEXT]),
  async (message) => {
    await enterSunoState(message.from_user.id, message);
  }
);

sunoRouter.callbackQuery(
  StartWithQuery('suno-generate'),
  async (callbackQuery) => {
    await enterSunoState(callbackQuery.from_user.id, callbackQuery.message);
  }
);

// Cancel Suno generate mode
sunoRouter.callbackQuery(
  StartWithQuery('cancel-suno-generate'),
  async (callbackQuery) => {
    await stateService.setCurrentState(callbackQuery.from_user.id, StateTypes.Default);
    await callbackQuery.message.delete();
    await callbackQuery.answer('Режим генерации музыки в Suno успешно отменён!');
  }
);

// Enter Suno state helper
async function enterSunoState(userId, message) {
  await stateService.setCurrentState(userId, StateTypes.Suno);
  await message.answer(
    `*Активирован режим* генерации музыки в *Suno*.

*Следующее ваше сообщение будет интерпретировано как промпт для Suno* и после отправки сообщения будет запущена генерация музыки, которая будет стоить *5000⚡️*.

Опишите в следующем сообщении музыкальную композицию 🎵 (*не более 200 символов*), которую вы хотите сгенерировать или отмените если передумали.`,
    {
      parse_mode: 'Markdown',
      reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
        new InlineKeyboardButton({ text: 'Отмена ❌', callback_data: 'cancel-suno-generate' })
      ]] })
    }
  );
}
