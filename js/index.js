import { botRun } from './bot/bot_run.js';

(async () => {
  console.info('Starting bot...');
  try {
    await botRun();
  } catch (err) {
    console.error('Bot encountered an error:', err);
    process.exit(1);
  }
})();
