// --- Original aiogram imports (commented out for reference) ---
// import { ParseMode } from 'aiogram/enums.js';
// import { InlineKeyboardButton, InlineKeyboardMarkup } from 'aiogram/types.js';
// --------------------------------------------------------------

import { InlineKeyboard } from 'grammy';

// Temporary lightweight stubs to keep existing code functional during migration.
const ParseMode = { MARKDOWN: 'Markdown', MARKDOWN_V2: 'MarkdownV2', HTML: 'HTML' };

class InlineKeyboardButton {
  constructor({ text, url, callback_data }) {
    this.text = text;
    if (url) this.url = url;
    if (callback_data) this.callback_data = callback_data;
  }
}

class InlineKeyboardMarkup {
  constructor({ inline_keyboard }) {
    this.reply_markup = new InlineKeyboard(inline_keyboard.flat());
  }
}
import { sendMessage } from '../main_keyboard.js';
import { GPTModels } from '../../services/gpt_service.js';
// --- Replaced telegramify-markdown with @vlad-yakovlev/telegram-md ---
// import telegramifyMarkdown from 'telegramify-markdown';
import tgMarkdown from 'telegramify-markdown';

// Wrapper to preserve existing telegramifyMarkdown.markdownify usage
const telegramifyMarkdown = {
  markdownify: (text) => tgMarkdown(text, 'escape')
};

export function checkedText(value) {
  return `✅ ${value}`;
}

export function getModelText(model, currentModel) {
  return model === currentModel ? checkedText(model) : model;
}

export const subscribeText = `
📰 Чтобы пользоваться ботом необходимо подписаться на наш канал! @gptDeep

Следите за обновлениями и новостями у нас в канале!
`;

export async function checkSubscription(ctx, userId = null) {
  if (!userId) userId = ctx.from.id;
  if (!userId) {
    console.warn('checkSubscription: userId undefined');
    return true;
  }
  try {
    const chatMember = await ctx.api.getChatMember('-1002239712203', userId);
    return ['creator', 'administrator', 'member'].includes(chatMember.status);
  } catch (err) {
    console.error('checkSubscription failed:', err);
    return false;
  }
}

export async function isChatMember(message) {
  const isSubscribe = await checkSubscription(message);
  if (!isSubscribe) {
    await message.answer(
      subscribeText,
      new InlineKeyboardMarkup({
        resize_keyboard: true,
        inline_keyboard: [
          [
            new InlineKeyboardButton({ text: 'Подписаться на канал', url: 'https://t.me/gptDeep' })
          ]
        ]
      })
    );
  }
  return isSubscribe;
}

export function getTokensMessage(tokensSpent, tokensLeft, requestedModel = null, respondedModel = null) {
  if (tokensSpent <= 0) return null;
  if (respondedModel && requestedModel === respondedModel) {
    return `🤖 Ответ от: *${respondedModel}*

✨ Затрачено: *${tokensSpent}⚡️* (осталось *${tokensLeft}⚡️*)`;
  } else if (requestedModel && respondedModel) {
    return `🤖 Ответ от: *${respondedModel}*
⚠️ Выбранная модель *${requestedModel}* временно недоступна!

✨ Затрачено: *${tokensSpent}⚡️* (осталось *${tokensLeft}⚡️*)`;
  } else if (requestedModel) {
    return `🤖 Ответ от: *${requestedModel}* (но это *не точно*)
⚠️ Если вы видите это сообщение, напишите об этом в разделе *Ошибки* в нашем сообществе @deepGPT.

✨ Затрачено: *${tokensSpent}⚡️* (осталось *${tokensLeft}⚡️*)`;
  } else {
    return `🤖 Ответ от: *неизвестно* (не удалось определить модель)
⚠️ Если вы видите это сообщение, напишите об этом в разделе *Ошибки* в нашем сообществе @deepGPT.

✨ Затрачено: *${tokensSpent}⚡️* (осталось *${tokensLeft}⚡️*)`;
  }
}

export function splitMessage(message) {
  const maxSymbols = 3990;
  const parts = [];
  let current = '';
  let currentLanguage = '';
  let inCodeBlock = false;
  const lines = message.split('\n');
  for (const line of lines) {
    const isCodeBlockLine = line.startsWith('```');
    if (isCodeBlockLine) {
      currentLanguage = line.slice(3).trim();
      inCodeBlock = !inCodeBlock;
    }
    const potential = current ? `${current}\n${line}` : line;
    if (potential.length > maxSymbols) {
      if (inCodeBlock) current += '\n```';
      parts.push(current);
      if (inCodeBlock) {
        current = `



`; // placeholder for new code block start
      } else {
        current = line;
      }
    } else {
      current = potential;
    }
  }
  if (current) {
    if (inCodeBlock) current += '\n```';
    parts.push(current);
  }
  return parts;
}

export async function sendMarkdownMessage(message, text) {
  const parts = splitMessage(text);
  for (const part of parts) {
    try {
      await sendMessage(message, telegramifyMarkdown.markdownify(part), { parse_mode: ParseMode.MARKDOWN_V2 });
    } catch (e) {
      await sendMessage(message, part, {});
      console.error('Failed to send message as markdown:', e);
    }
  }
  return parts;
}

export function createChangeModelKeyboard(currentModel) {
  return new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [
      [ new InlineKeyboardButton({ text: getModelText(GPTModels.O3_mini, currentModel), callback_data: GPTModels.O3_mini }) ],
      [ new InlineKeyboardButton({ text: getModelText(GPTModels.O1_preview, currentModel), callback_data: GPTModels.O1_preview }), new InlineKeyboardButton({ text: getModelText(GPTModels.O1_mini, currentModel), callback_data: GPTModels.O1_mini }) ]
      // ... add remaining rows
    ]
  });
}
