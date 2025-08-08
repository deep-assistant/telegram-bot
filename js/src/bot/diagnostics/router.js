import { Router } from 'aiogram'; // Stub import
import { TextCommand } from '../filters.js';
import { sendMarkdownMessage } from '../gpt/utils.js';
import { HERE_AND_NOW_COMMAND } from '../commands.js';

export const diagnosticsRouter = new Router();

diagnosticsRouter.message(TextCommand([HERE_AND_NOW_COMMAND]), async (message) => {
  const startTime = new Date();
  const user = message.from_user;
  const chat = message.chat;

  // Collect user info
  const userInfo = [];
  if (user.id != null) userInfo.push(`User ID: \`${user.id}\``);
  if (user.full_name?.trim()) userInfo.push(`Full Name: \`${user.full_name.trim()}\``);
  if (user.username) userInfo.push(`Username: \`@${user.username}\``);
  if (user.is_bot != null) userInfo.push(`Is Bot: \`${user.is_bot ? 'Yes' : 'No'}\``);
  if (user.language_code) userInfo.push(`Language: \`${user.language_code}\``);
  if (user.is_premium != null) userInfo.push(`Premium: \`${user.is_premium ? 'Yes' : 'No'}\``);

  // Collect chat info
  const chatInfo = [];
  if (chat.id) chatInfo.push(`Chat ID: \`${chat.id}\``);
  if (chat.type) chatInfo.push(`Type: \`${chat.type}\``);
  if (chat.title) chatInfo.push(`Title: \`${chat.title}\``);
  if (chat.username) chatInfo.push(`Username: \`@${chat.username}\``);

  // Timestamps and metrics
  const telegramTime = new Date(message.date);
  const botTime = new Date();
  const latency = (startTime - telegramTime) / 1000;

  const responseLines = ['**Here and Now**:'];
  if (userInfo.length) {
    responseLines.push('**User Info**:');
    responseLines.push(...userInfo);
  }
  if (chatInfo.length) {
    responseLines.push('\n**Chat Info**:');
    responseLines.push(...chatInfo);
  }
  responseLines.push('\n**Timestamps**:');
  responseLines.push(`Telegram Time: **${telegramTime.toUTCString()}**`);
  responseLines.push(`Bot Time: **${botTime.toUTCString()}**`);
  responseLines.push('\n**Performance Metrics**:');
  responseLines.push(`Latency: **${latency.toFixed(2)}** seconds`);

  const endTime = new Date();
  const processingTime = (endTime - startTime) / 1000;
  responseLines.push(`Processing Time: **${processingTime.toFixed(2)}** seconds`);

  const response = responseLines.join('\n');
  await sendMarkdownMessage(message, response);
});
