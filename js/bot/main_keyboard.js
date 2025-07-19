import { Keyboard } from 'grammy';
import { createLogger } from '../utils/logger.js';
import { config } from '../config.js';
import tgMarkdown from 'telegramify-markdown';

const log = createLogger('main_keyboard');
const chatMessageCounts = {};
const FIRST_MESSAGES_LIMIT = 3;

export function createMainKeyboard(ctx) {
  log.trace(`Creating main keyboard for user: ${ctx.from?.id}`);
  const keyboard = new Keyboard()
    .text(ctx.t('buttons.balance')).text(ctx.t('buttons.buy')).row()
    .text(ctx.t('buttons.model')).text(ctx.t('buttons.system')).row()
    .text(ctx.t('buttons.suno')).text(ctx.t('buttons.image')).row()
    .text(ctx.t('buttons.clear')).text(ctx.t('buttons.history')).row()
    .text(ctx.t('buttons.referral'))
    .resized()
    .placeholder(ctx.t('main_keyboard.placeholder'));
  
  log.trace(`Keyboard created: ${JSON.stringify({
    keyboard: keyboard.keyboard,
    resize_keyboard: keyboard.resize_keyboard,
    input_field_placeholder: keyboard.input_field_placeholder
  })}`);
  
  return keyboard;
}

export async function sendMessage(ctx, text, options = {}) {
  log.trace(`sendMessage called with: chatId=${ctx.chat?.id}, userId=${ctx.from?.id}, textType=${typeof text}, textPreview=${typeof text === 'string' ? text.slice(0, 100) : 'object'}, options=${JSON.stringify(Object.keys(options))}`);

  if (typeof text === 'object' && text !== null && 'text' in text) {
    const tmp = text;
    text = tmp.text;
    const { text: _, ...rest } = tmp;
    options = { ...options, ...rest };
    log.trace(`Extracted text from object: ${text.slice(0, 100)}`);
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

  log.debug('sendMessage', {
    messageType: typeof text,
    messagePreview: text.slice?.(0,50) || text,
    reply_markup: options.reply_markup ? {
      keyboard: options.reply_markup.keyboard,
      resize_keyboard: options.reply_markup.resize_keyboard,
      input_field_placeholder: options.reply_markup.input_field_placeholder
    } : undefined,
    parse_mode: options.parse_mode
  });
  return ctx.reply(text, options);
}
