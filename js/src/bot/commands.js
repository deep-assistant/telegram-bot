export const PAYMENT_COMMAND_START = '/donut';
export const PAYMENT_COMMAND_TEXT = '💖 Пожертвование';
export const BALANCE_PAYMENT_COMMAND_TEXT = '💎 Пополнить баланс';
export const BALANCE_PAYMENT_COMMAND_START = '/buy';
export const REFERRAL_COMMAND = '/referral';
export const CHANGE_MODEL_COMMAND = '/model';
export const CHANGE_MODEL_TEXT = '🛠️ Сменить модель';
export const CHANGE_SYSTEM_MESSAGE_COMMAND = '/system';
export const CHANGE_SYSTEM_MESSAGE_TEXT = '⚙️ Сменить Режим';
export const BALANCE_TEXT = '✨ Баланс';
export const BALANCE_COMMAND = '/balance';
export const CLEAR_TEXT = '🧹 Очистить контекст';
export const CLEAR_COMMAND = '/clear';
export const MULTIMODAL_COMMAND = '/multimodal';
export const GET_HISTORY_COMMAND = '/history';
export const GET_HISTORY_TEXT = '📖 История диалога';
export const HELP_COMMAND = '/help';
export const APP_COMMAND = '/app';
export const HELP_TEXT = '🆘 Помощь';
export const REFERRAL_COMMAND_TEXT = '🔗 Реферальная ссылка';
export const IMAGES_COMMAND = '/image';
export const IMAGES_COMMAND_TEXT = '🖼️ Генерация картинки';
export const GET_REMOVE_BACKGROUND_COMMAND = '/remove_background';
export const SUNO_COMMAND = '/suno';
export const SUNO_TEXT = '🎵 Генерация музыки';
export const HERE_AND_NOW_COMMAND = '/here_and_now';
export const API_COMMAND = '/api';

export const ALL_COMMANDS = [
  PAYMENT_COMMAND_START,
  PAYMENT_COMMAND_TEXT,
  BALANCE_PAYMENT_COMMAND_TEXT,
  BALANCE_PAYMENT_COMMAND_START,
  REFERRAL_COMMAND,
  CHANGE_MODEL_COMMAND,
  CHANGE_MODEL_TEXT,
  CHANGE_SYSTEM_MESSAGE_COMMAND,
  CHANGE_SYSTEM_MESSAGE_TEXT,
  BALANCE_TEXT,
  BALANCE_COMMAND,
  CLEAR_TEXT,
  CLEAR_COMMAND,
  MULTIMODAL_COMMAND,
  GET_HISTORY_COMMAND,
  GET_HISTORY_TEXT,
  HELP_COMMAND,
  APP_COMMAND,
  HELP_TEXT,
  REFERRAL_COMMAND_TEXT,
  IMAGES_COMMAND,
  IMAGES_COMMAND_TEXT,
  GET_REMOVE_BACKGROUND_COMMAND,
  SUNO_COMMAND,
  SUNO_TEXT,
  HERE_AND_NOW_COMMAND,
  API_COMMAND
];

// --- Helper functions for backward-compatibility with aiogram version ---
export const helpText = () => HELP_TEXT;
export const helpCommand = () => HELP_COMMAND;
export const appCommand = () => APP_COMMAND;
