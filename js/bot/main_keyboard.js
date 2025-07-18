import { Keyboard } from 'grammy';
import {
  BALANCE_TEXT,
  BALANCE_PAYMENT_COMMAND_TEXT,
  CHANGE_MODEL_TEXT,
  CHANGE_SYSTEM_MESSAGE_TEXT,
  SUNO_TEXT,
  IMAGES_COMMAND_TEXT,
  CLEAR_TEXT,
  GET_HISTORY_TEXT,
  REFERRAL_COMMAND_TEXT
} from './commands.js';
import tgMarkdown from 'telegramify-markdown';

const chatMessageCounts = {};
const FIRST_MESSAGES_LIMIT = 3;

export function createMainKeyboard() {
  return new Keyboard()
    .text(BALANCE_TEXT).text(BALANCE_PAYMENT_COMMAND_TEXT).row()
    .text(CHANGE_MODEL_TEXT).text(CHANGE_SYSTEM_MESSAGE_TEXT).row()
    .text(SUNO_TEXT).text(IMAGES_COMMAND_TEXT).row()
    .text(CLEAR_TEXT).text(GET_HISTORY_TEXT).row()
    .text(REFERRAL_COMMAND_TEXT)
    .resized()
    .placeholder('💬 Задай свой вопрос');
}

export async function sendMessage(ctx, text, options = {}) {
  if (typeof text === 'object' && text !== null && 'text' in text) {
    const tmp = text;
    text = tmp.text;
    const { text: _, ...rest } = tmp;
    options = { ...options, ...rest };
  }

  const chatId = ctx.chat.id;
  chatMessageCounts[chatId] = (chatMessageCounts[chatId] || 0) + 1;

  if (!options.reply_markup && chatMessageCounts[chatId] <= FIRST_MESSAGES_LIMIT) {
    options.reply_markup = createMainKeyboard();
  }

  if (!('parse_mode' in options)) {
    options.parse_mode = 'MarkdownV2';
  }

  if (options.parse_mode === 'MarkdownV2' && typeof text === 'string' && !options.no_build) {
    text = tgMarkdown(text, 'escape');
  }

  console.debug('sendMessage', typeof text, text.slice?.(0,50) || text, options);
  return ctx.reply(text, options);
}
