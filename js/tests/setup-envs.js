import { Bot } from 'grammy';
import { config } from '../src/config.js';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const dotenvx = require('@dotenvx/dotenvx');

async function getBotInfo() {
  if (!config.botToken) {
    throw new Error('TOKEN is not set in .env file');
  }

  console.log('🤖 Getting bot info from Telegram API...');
  
  const bot = new Bot(config.botToken);
  try {
    const me = await bot.api.getMe();
    console.log(`✅ Bot found: ${me.first_name} (@${me.username})`);
    return me;
  } catch (error) {
    console.error('❌ Failed to get bot info:', error.message);
    throw error;
  }
}

async function updateEnvFile(botInfo) {
  const botName = `@${botInfo.username}`;
  
  dotenvx.set('TELEGRAM_BOT_NAME', botName, { path: '.env', encrypt: false });
  console.log(`✅ Updated .env with TELEGRAM_BOT_NAME=${botName}`);
}

async function setupEnvs() {
  try {
    const botInfo = await getBotInfo();
    await updateEnvFile(botInfo);
    console.log('🎉 Environment setup complete!');
  } catch (error) {
    console.error('❌ Setup failed:', error.message);
    process.exit(1);
  }
}

if (import.meta.main) {
  setupEnvs().catch(console.error);
}