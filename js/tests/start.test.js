import { usingTelegram } from './user-bot.js';
import { config } from '../src/config.js';

async function testSendStartMessage() {
  console.log('🚀 Testing /start message sending...');
  
  await usingTelegram(async ({ client }) => {
    await client.sendMessage(config.telegramBotName, { message: '/start' });
    console.log(`✅ Sent /start message to ${config.telegramBotName}`);
  });
}

if (import.meta.main) {
  testSendStartMessage().catch(console.error);
}