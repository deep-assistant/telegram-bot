import { Keyboard } from 'grammy';
import tgMarkdown from 'telegramify-markdown';

const chatMessageCounts = {};
const FIRST_MESSAGES_LIMIT = 3;

export function createMainKeyboard(ctx) {
  return new Keyboard()
    .text(ctx.t('main_keyboard.balance')).text(ctx.t('main_keyboard.buy')).row()
    .text(ctx.t('main_keyboard.model')).text(ctx.t('main_keyboard.system')).row()
    .text(ctx.t('main_keyboard.suno')).text(ctx.t('main_keyboard.image')).row()
    .text(ctx.t('main_keyboard.clear')).text(ctx.t('main_keyboard.history')).row()
    .text(ctx.t('main_keyboard.referral'))
    .resized()
    .placeholder(ctx.t('main_keyboard.placeholder'));
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
    options.reply_markup = createMainKeyboard(ctx);
  }

  if (!('parse_mode' in options)) {
    options.parse_mode = 'MarkdownV2';
  }

  if (options.parse_mode === 'MarkdownV2' && typeof text === 'string' && !options.no_build) {
    text = tgMarkdown(text, 'escape');
  }

  console.debug('sendMessage', typeof text, text.slice?.(0,50) || text, {
    reply_markup: options.reply_markup ? {
      keyboard: options.reply_markup.keyboard,
      resize_keyboard: options.reply_markup.resize_keyboard,
      input_field_placeholder: options.reply_markup.input_field_placeholder
    } : undefined,
    parse_mode: options.parse_mode
  });
  return ctx.reply(text, options);
}
