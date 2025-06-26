import { Router } from 'aiogram'; // Stub import
import { InlineKeyboardButton, InlineKeyboardMarkup } from 'aiogram/types.js';

import { API_COMMAND } from '../commands.js';
import { TextCommand, TextCommandQuery } from '../filters.js';
import { tokenizeService } from '../../services/index.js';

export const apiRouter = new Router();

function getApiMessage(token) {
  return {
    text: `API KEY: \`${token.id}\` \n` +
          `API URL: https://api.deep-foundation.tech/v1/ \n` +
          `API URL Whisper: https://api.deep-foundation.tech/v1/audio/transcriptions  \n` +
          `API URL Completions: https://api.deep-foundation.tech/v1/chat/completions \n\n` +
          `Ваш баланс: ${token.tokens_gpt}⚡️️ \n\n` +
          `https://github.com/deep-foundation/deep-gpt/blob/main/docs.md - 📄 Документация по работе с API`,
    reply_markup: {
      resize_keyboard: true,
      inline_keyboard: [
        [
          { text: 'Перегенерировать токен 🔄', callback_data: 'regenerate_token' }
        ]
      ]
    }
  };
}

// Handle /api command
apiRouter.message(TextCommand([API_COMMAND]), async (message) => {
  const token = await tokenizeService.get_token(message.from_user.id);
  await message.answer(getApiMessage(token));
});

// Handle regenerate token callback
apiRouter.callbackQuery(
  TextCommandQuery(['regenerate_token']),
  async (callbackQuery) => {
    const token = await tokenizeService.regenerate_api_token(callbackQuery.from_user.id);
    // mimic async sleep
    await new Promise(r => setTimeout(r, 1000));
    await callbackQuery.message.edit_text(getApiMessage(token));
    await callbackQuery.answer('✅ Токен успешно обновлен!');
  }
);
