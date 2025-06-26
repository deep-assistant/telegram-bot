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

const chatMessageCounts = {};
const FIRST_MESSAGES_LIMIT = 3;

export function createMainKeyboard() {
  return {
    resize_keyboard: true,
    keyboard: [
      [
        { text: BALANCE_TEXT },
        { text: BALANCE_PAYMENT_COMMAND_TEXT }
      ],
      [
        { text: CHANGE_MODEL_TEXT },
        { text: CHANGE_SYSTEM_MESSAGE_TEXT }
      ],
      [
        { text: SUNO_TEXT },
        { text: IMAGES_COMMAND_TEXT }
      ],
      [
        { text: CLEAR_TEXT },
        { text: GET_HISTORY_TEXT }
      ],
      [
        { text: REFERRAL_COMMAND_TEXT }
      ]
    ],
    input_field_placeholder: '💬 Задай свой вопрос'
  };
}

export async function sendMessage(ctx, text, options = {}) {
  // Determine chat ID and reply function
  const chatId = ctx.chat?.id ?? ctx.message?.chat?.id;
  const answer = ctx.chat
    ? ctx.reply.bind(ctx)
    : ctx.message
      ? ctx.message.reply.bind(ctx.message)
      : null;
  if (!answer) {
    throw new Error('First argument must be a message or callbackQuery-like object');
  }

  // Track message count
  chatMessageCounts[chatId] = (chatMessageCounts[chatId] || 0) + 1;

  // Assign keyboard for first messages if not provided
  if (!options.reply_markup && chatMessageCounts[chatId] <= FIRST_MESSAGES_LIMIT) {
    options.reply_markup = createMainKeyboard();
  }

  return answer(text, options);
}
