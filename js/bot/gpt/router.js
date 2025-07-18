import { Composer } from 'grammy';
import fs from 'fs/promises';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

import { config } from '../../config.js';
// import { agreementHandler } from '../agreement/router.js';
import { TextCommand, TextCommandQuery, Document, Photo, Voice, Audio, Video, StateCommand, StartWithQuery } from '../filters.js';
import {
  CHANGE_MODEL_COMMAND,
  CHANGE_SYSTEM_MESSAGE_COMMAND,
  CHANGE_SYSTEM_MESSAGE_TEXT,
  CHANGE_MODEL_TEXT,
  BALANCE_TEXT,
  BALANCE_COMMAND,
  CLEAR_COMMAND,
  CLEAR_TEXT,
  GET_HISTORY_COMMAND,
  GET_HISTORY_TEXT
} from '../commands.js';
import { getSystemMessage, systemMessagesList, createSystemMessageKeyboard } from './system_messages.js';
import { isChatMember, sendMarkdownMessage, getTokensMessage, createChangeModelKeyboard } from './utils.js';
import { formatImageFromRequest } from '../../services/image_utils.js';
import { asyncPost, asyncGet } from '../../services/utils.js';
import {
  gptService,
  GPTModels,
  completionsService,
  tokenizeService,
  referralsService,
  stateService,
  StateTypes,
  systemMessage
} from '../../services/index.js';
import { DIALOG_CONTEXT_CLEAR_FAILED_DEFAULT_ERROR_MESSAGE } from '../constants.js';

export const gptRouter = new Composer();
let questionAnswer = false;

// Helper to send markdown content as document if too large
async function answerMarkdownFile(message, mdContent) {
  const dir = path.join(process.cwd(), 'markdown_files');
  await fs.mkdir(dir, { recursive: true });
  const filePath = path.join(dir, `${uuidv4()}.md`);
  await fs.writeFile(filePath, mdContent, 'utf8');
  await message.answerDocument(FSInputFile(filePath), { caption: 'Сообщение в формате markdown' });
  await fs.unlink(filePath);
}

// Helper to get URLs for photo objects
async function getPhotosLinks(message, photos) {
  const images = [];
  for (const photo of photos) {
    const fileInfo = await message.bot.get_file({ file_id: photo.file_id });
    const fileUrl = `https://api.telegram.org/file/bot${config.TOKEN}/${fileInfo.file_path}`;
    images.push({ type: 'image_url', image_url: { url: fileUrl } });
  }
  return images;
}

// Detect GPT model from string
function detectModel(model) {
  if (!model) return null;
  for (const val of Object.values(GPTModels)) {
    if (model.includes(val)) return val;
  }
  if (model.includes('auto')) return GPTModels.GPT_Auto;
  if (model.includes('deepseek-r1')) return GPTModels.DeepSeek_Reasoner;
  if (model.includes('gpt-4-gizmo')) return GPTModels.GPT_4_Unofficial;
  if (model.includes('Llama-3.1-405B')) return GPTModels.Llama3_1_405B;
  if (model.includes('Llama-3.1-70B')) return GPTModels.Llama3_1_70B;
  if (model.includes('Llama-3.1-8B')) return GPTModels.Llama3_1_8B;
  if (model.includes('gpt-3.5-turbo')) return GPTModels.GPT_3_5;
  if (model.includes('gpt-4o-plus')) return GPTModels.GPT_4o;
  return null;
}

// Core GPT request executor
async function handleGptRequest(message, text) {
  const userId = message.from_user.id;
  const loadingMessage = await message.answer('**⌛️Ожидайте ответ...**');
  try {
    // Agreement and subscription checks
    // const agreed = await agreementHandler(message);
    // if (!agreed) return;
    const subscribed = await isChatMember(message);
    if (!subscribed) return;
    if (!stateService.is_default_state(userId)) return;

    const chatId = message.chat.id;
    const botModel = gptService.get_current_model(userId);
    const gptModel = gptService.get_mapping_gpt_model(userId);
    await message.bot.send_chat_action(chatId, 'typing');

    // System message and token check
    let sysMsg = gptService.get_current_system_message(userId);
    const tokensBefore = await tokenizeService.get_tokens(userId);
    if ((tokensBefore.tokens || 0) <= 0) {
      await message.answer(
        `/balance - ✨ Проверить Баланс\n/buy - 💎 Пополнить баланс\n/referral - 👥 Пригласить друга`
      );
      return;
    }
    sysMsg = getSystemMessage(sysMsg);
    questionAnswer = (sysMsg === 'question-answer');

    const answer = await completionsService.query_chatgpt(
      userId, text, sysMsg, gptModel, botModel, questionAnswer
    );
    // Log and detect models
    const requestedVal = detectModel(gptModel);
    const respondedVal = detectModel(answer.model);

    if (!answer.success) {
      await message.answer(answer.response);
      return;
    }

    const tokensAfter = await tokenizeService.get_tokens(userId);
    const { image, text: respText } = formatImageFromRequest(answer.response);
    const parts = await sendMarkdownMessage(message, respText);
    if (parts.length > 1) await answerMarkdownFile(message, respText);
    if (image) {
      await message.answerPhoto(image);
      await sendPhotoAsFile(message, image, 'Вот картинка в оригинальном качестве');
    }

    await loadingMessage.delete();
    const spent = (tokensBefore.tokens || 0) - (tokensAfter.tokens || 0);
    const tokenMsg = await message.answer(
      getTokensMessage(spent, tokensAfter.tokens, requestedVal, respondedVal)
    );
    if (['group', 'supergroup'].includes(message.chat.type)) {
      await new Promise(r => setTimeout(r, 2000));
      await tokenMsg.delete();
    }
  } catch (err) {
    console.error(err);
  }
}

// Replace stub with actual invocation for unhandled text messages
gptRouter.message(TextCommand([]), async (message) => {
  await handleGptRequest(message, message.text || '');
});

// Simple video handler (logs video info)
gptRouter.message(Video(), async (message) => {
  console.log('Received video:', message.video);
});

// Photo handler: processes media groups and single photos
gptRouter.message(Photo(), async (message, album) => {
  // In groups, ensure bot is mentioned
  if (['group', 'supergroup'].includes(message.chat.type)) {
    if (!message.entities) return;
    const mentioned = message.entities.some(e => e.type === 'mention');
    if (!mentioned) return;
  }
  // Extract highest-quality photos
  const photos = album.map(item => item.photo[item.photo.length - 1]);
  const userId = message.from_user.id;
  if (!stateService.is_default_state(userId)) return;
  const tokens = await tokenizeService.get_tokens(userId);
  if ((tokens.tokens || 0) < 0) {
    await message.answer(
      '/balance - ✨ Проверить Баланс\n/buy - 💎 Пополнить баланс\n/referral - 👥 Пригласить друга'
    );
    stateService.set_current_state(userId, StateTypes.Default);
    return;
  }
  const subscribed = await isChatMember(message);
  if (!subscribed) return;
  const text = message.caption || 'Опиши';
  await message.bot.send_chat_action(message.chat.id, 'typing');
  const content = await getPhotosLinks(message, photos);
  content.push({ type: 'text', text });
  await handleGptRequest(message, content);
});

// Stub for voice transcription
async function transcribeVoice(userId, voiceFileUrl) {
  // TODO: integrate with transcription API
  return { success: false, text: 'Transcription not implemented.' };
}

// Voice and Audio handler: transcribe and process
gptRouter.message(Voice(), async (message) => {
  // Group mention check
  if (['group', 'supergroup'].includes(message.chat.type)) {
    if (!message.entities) return;
    const mentioned = message.entities.some(e => e.type === 'mention');
    if (!mentioned) return;
  }
  const userId = message.from_user.id;
  if (!(await stateService.isDefaultState(userId))) return;
  const tokens = await tokenizeService.get_tokens(userId);
  if ((tokens.tokens || 0) < 0) {
    await message.answer(
      '/balance - ✨ Проверить Баланс\n/buy - 💎 Пополнить баланс\n/referral - 👥 Пригласить друга'
    );
    await stateService.setCurrentState(userId, StateTypes.Default);
    return;
  }
  const subscribed = await isChatMember(message);
  if (!subscribed) return;

  const msgData = message.voice || message.audio;
  const fileInfo = await message.bot.get_file({ file_id: msgData.file_id });
  const fileUrl = `https://api.telegram.org/file/bot${config.TOKEN}/${fileInfo.file_path}`;
  const response = await transcribeVoice(userId, fileUrl);
  if (response.success) {
    // TODO: respect state Transcribe
    await handleGptRequest(message, response.text);
  } else {
    await message.answer(response.text);
  }
});

// TODO: implement Audio handler similar to Voice handler for audio messages
// gptRouter.message(Audio(), async (message) => { ... });

// TODO: implement other handlers:
// - getPhotosLinks (async function to retrieve photo links)
// - Video and Photo message handlers
// - Voice and Audio message handlers (transcribe)
// - Document handlers
// - /balance command handler
// - /clear context handler
// - Change model and system message flows
// - History command handler
// - Fallback completion handler

// Clear context handler
gptRouter.message(TextCommand([CLEAR_COMMAND, CLEAR_TEXT]), async (ctx) => {
  const userId = ctx.from.id;
  try {
    const response = await tokenizeService.clear_dialog(userId);
    if (!response || !response.status) {
      await ctx.reply('Диалог уже пуст!');
      return;
    }
  } catch (e) {
    await ctx.reply(DIALOG_CONTEXT_CLEAR_FAILED_DEFAULT_ERROR_MESSAGE);
    console.error('Error clearing dialog context:', e);
    return;
  }
  await ctx.reply('Контекст диалога успешно очищен! 👌🏻');
});

// Balance command handler
gptRouter.message(TextCommand([BALANCE_TEXT, BALANCE_COMMAND]), async (ctx) => {
  const userId = ctx.from.id;
  // Fetch token and referral info
  const gptTokens = await tokenizeService.get_tokens(userId);
  const referral = await referralsService.get_referral(userId);

  // Calculate next refill time
  const lastUpdate = new Date(referral.lastUpdate);
  const newDate = new Date(lastUpdate.getTime() + 24 * 60 * 60 * 1000);
  const currentDate = new Date();

  function getDate() {
    if (newDate.getDate() === currentDate.getDate()) {
      return `Сегодня в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
    } else {
      return `Завтра в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
    }
  }

  function getDateLine() {
    if ((gptTokens.tokens || 0) >= 30000) {
      return '🕒 Автопополнение доступно, если меньше *30000*⚡️';
    }
    return `🕒 Следующее автопополнение будет: *${getDate()}*`;
  }

  function acceptAccount() {
    return referral.isActivated
      ? '🔑 Ваш аккаунт подтвержден!'
      : '🔑 Ваш аккаунт не подтвержден, зайдите через сутки и совершите любое действие!';
  }

  // Send balance info
  await ctx.reply(`👩🏻‍💻 Количество рефералов: *${referral.children.length}*
🤑 Ежедневное автопополнение 🔋: *${referral.award}⚡️*
${acceptAccount()}

${getDateLine()}

💵 Текущий баланс: *${gptTokens.tokens || 0}⚡️*`);
});

// History command handler
gptRouter.message(TextCommand([GET_HISTORY_COMMAND, GET_HISTORY_TEXT]), async (message) => {
  // Agreement and subscription checks
  // const agreed = await agreementHandler(message);
  // if (!agreed) return;
  const subscribed = await isChatMember(message);
  if (!subscribed) return;
  const userId = message.from_user.id;
  const history = await tokenizeService.history(userId);
  if (history.status === 404) {
    await message.answer('История диалога пуста.');
    return;
  }
  if (!history || !history.response) {
    await message.answer('Ошибка 😔: Не удалось получить историю диалога!');
    return;
  }
  const messages = history.response.messages;
  const jsonData = JSON.stringify(messages, null, 2);
  // Send as document
  const file = FSInputFile(Buffer.from(jsonData, 'utf-8'), { filename: 'dialog_history.json' });
  await message.answerDocument(file);
  // Clean up
  await new Promise(r => setTimeout(r, 500));
  await message.delete();
});

// Bot command handler
gptRouter.message(TextCommand(['/bot', '/bot@DeepGPTBot']), async (message) => {
  console.log(`Command received: ${message.text}`);
  let text = message.text || '';
  if (message.reply_to_message && message.reply_to_message.text) {
    text += `\n\n${message.reply_to_message.text}`;
  }
  await handleGptRequest(message, text);
});

// Change system message command handler
gptRouter.message(TextCommand([CHANGE_SYSTEM_MESSAGE_COMMAND, CHANGE_SYSTEM_MESSAGE_TEXT]), async (message) => {
  // const agreed = await agreementHandler(message);
  // if (!agreed) return;
  const subscribed = await isChatMember(message);
  if (!subscribed) return;
  const userId = message.from_user.id;
  let currentSystemMessage = gptService.get_current_system_message(userId);
  if (!systemMessagesList.includes(currentSystemMessage)) {
    currentSystemMessage = SystemMessages.Custom;
    gptService.set_current_system_message(userId, currentSystemMessage);
  }
  await message.answer(
    'Установи режим работы бота: ⚙️',
    { reply_markup: createSystemMessageKeyboard(currentSystemMessage) }
  );
  await new Promise(r => setTimeout(r, 500));
  await message.delete();
});

// Change model command handler
gptRouter.message(TextCommand([CHANGE_MODEL_COMMAND, CHANGE_MODEL_TEXT]), async (message) => {
  // const agreed = await agreementHandler(message);
  // if (!agreed) return;
  const subscribed = await isChatMember(message);
  if (!subscribed) return;
  const userId = message.from_user.id;
  const currentModel = gptService.get_current_model(userId);
  const infoText = `Выберите модель: 🤖\n*o3-mini:* ... \n*GPT-3.5-turbo:* ...`;
  await message.answer(infoText, { reply_markup: createChangeModelKeyboard(currentModel) });
  await new Promise(r => setTimeout(r, 500));
  await message.delete();
});

// State to capture custom system message
gptRouter.message(StateCommand(StateTypes.SystemMessageEditing), async (message) => {
  const userId = message.from_user.id;
  gptService.set_current_system_message(userId, message.text);
  await systemMessage.edit_system_message(userId, message.text);
  await stateService.setCurrentState(userId, StateTypes.Default);
  await new Promise(r => setTimeout(r, 500));
  await message.answer('Режим успешно изменён!');
  await message.delete();
});

// Cancel system message editing
gptRouter.callbackQuery(StartWithQuery('cancel-system-edit'), async (callbackQuery) => {
  const parts = callbackQuery.data.split(' ');
  const systemMsg = parts.slice(1).join(' ');
  const userId = callbackQuery.from_user.id;
  gptService.set_current_system_message(userId, systemMsg);
  await stateService.setCurrentState(userId, StateTypes.Default);
  await callbackQuery.message.delete();
  await callbackQuery.answer('Успешно отменено!');
});

// Handle system message selection
gptRouter.callbackQuery(TextCommandQuery(systemMessagesList), async (callbackQuery) => {
  const userId = callbackQuery.from_user.id;
  const sysMsg = callbackQuery.data;
  const currentSys = gptService.get_current_system_message(userId);
  if (sysMsg === currentSys && sysMsg !== SystemMessages.Custom) {
    await callbackQuery.answer('Данный режим уже выбран!');
    return;
  }
  if (sysMsg === SystemMessages.Custom) {
    await stateService.setCurrentState(userId, StateTypes.SystemMessageEditing);
  } else {
    gptService.set_current_system_message(userId, sysMsg);
  }
  await callbackQuery.answer();
});

// Handle model selection
gptRouter.callbackQuery(TextCommandQuery(Object.values(GPTModels)), async (callbackQuery) => {
  const userId = callbackQuery.from_user.id;
  gptService.set_current_model(userId, callbackQuery.data);
  await callbackQuery.answer('Модель успешно изменена!');
});

// Fallback completion handler for any other messages
gptRouter.message(async (message) => {
  // In groups, ensure bot is mentioned
  if (['group', 'supergroup'].includes(message.chat.type)) {
    if (!message.entities) return;
    const mentioned = message.entities.some(e => e.type === 'mention' && message.text?.substring(e.offset + 1, e.offset + e.length) === 'DeepGPTBot');
    if (!mentioned) return;
  }
  await handleGptRequest(message, message.text || '');
});

