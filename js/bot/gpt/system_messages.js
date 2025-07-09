import { InlineKeyboardButton, InlineKeyboardMarkup } from 'aiogram/types.js';
import { checkedText } from './utils.js';
import { SystemMessages } from '../../services/gpt_service.js';
import {
  defaultSystemMessage,
  happySystemMessage,
  softwareDeveloperSystemMessage,
  questionAnswerMode,
  promtDeep,
  transcribe
} from './db_system_message.js';

export const systemMessages = {
  [SystemMessages.Default]: defaultSystemMessage,
  [SystemMessages.Happy]: happySystemMessage,
  [SystemMessages.SoftwareDeveloper]: softwareDeveloperSystemMessage,
  [SystemMessages.DeepPromt]: promtDeep,
  [SystemMessages.QuestionAnswer]: questionAnswerMode,
  [SystemMessages.Transcribe]: transcribe
};

export const textSystemMessages = {
  [SystemMessages.Custom]: '💎 Указать свое',
  [SystemMessages.Default]: '🤖 Стандартный',
  [SystemMessages.Happy]: '🥳 Веселый',
  [SystemMessages.SoftwareDeveloper]: '👨‍💻 Программист',
  [SystemMessages.DeepPromt]: '🕳️ Wanderer from the Deep',
  [SystemMessages.QuestionAnswer]: '💬 Вопрос-ответ',
  [SystemMessages.Transcribe]: '🎤 Голос в текст'
};

export function getSystemMessage(value) {
  return systemMessages[value] || value;
}

export const systemMessagesList = Object.values(SystemMessages);

export function getSystemMessageText(systemMessage, currentSystemMessage) {
  if (systemMessage === currentSystemMessage) {
    return checkedText(systemMessage);
  }
  return systemMessage;
}

export function createSystemMessageKeyboard(currentSystemMessage) {
  return new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [
      [
        new InlineKeyboardButton({
          text: getSystemMessageText(
            textSystemMessages[SystemMessages.Custom],
            textSystemMessages[currentSystemMessage]
          ),
          callback_data: SystemMessages.Custom
        })
      ],
      [
        new InlineKeyboardButton({
          text: getSystemMessageText(
            textSystemMessages[SystemMessages.Default],
            textSystemMessages[currentSystemMessage]
          ),
          callback_data: SystemMessages.Default
        }),
        new InlineKeyboardButton({
          text: getSystemMessageText(
            textSystemMessages[SystemMessages.Happy],
            textSystemMessages[currentSystemMessage]
          ),
          callback_data: SystemMessages.Happy
        })
      ],
      [
        new InlineKeyboardButton({
          text: getSystemMessageText(
            textSystemMessages[SystemMessages.SoftwareDeveloper],
            textSystemMessages[currentSystemMessage]
          ),
          callback_data: SystemMessages.SoftwareDeveloper
        }),
        new InlineKeyboardButton({
          text: getSystemMessageText(
            textSystemMessages[SystemMessages.DeepPromt],
            textSystemMessages[currentSystemMessage]
          ),
          callback_data: SystemMessages.DeepPromt
        })
      ],
      [
        new InlineKeyboardButton({
          text: getSystemMessageText(
            textSystemMessages[SystemMessages.QuestionAnswer],
            textSystemMessages[currentSystemMessage]
          ),
          callback_data: SystemMessages.QuestionAnswer
        })
      ],
      [
        new InlineKeyboardButton({
          text: getSystemMessageText(
            textSystemMessages[SystemMessages.Transcribe],
            textSystemMessages[currentSystemMessage]
          ),
          callback_data: SystemMessages.Transcribe
        })
      ]
    ]
  });
}
