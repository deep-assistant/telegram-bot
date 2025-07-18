import { Bot } from 'grammy';
import { run } from '@grammyjs/runner';
import { config } from './config.js';
import { startRouter } from './bot/start/router.js';
import { AlbumMiddleware } from './bot/middlewares/AlbumMiddleware.js';
import { i18n } from './i18n.js';
import { createLogger } from './utils/logger.js';

const logger = createLogger('main');

async function startBot() {
  logger.info('Starting bot...');
  
  const bot = new Bot(config.BOT_TOKEN);
  
  // Add middlewares
  bot.use(i18n);
  bot.use(AlbumMiddleware);
  
  // Add routers
  bot.use(startRouter);
  
  // Error handling
  bot.catch((err) => {
    logger.error('Bot error:', err);
  });
  
  try {
    if (config.WEBHOOK_URL) {
      logger.info('Starting bot webhook...');
      await bot.api.setWebhook(config.WEBHOOK_URL);
      await bot.start();
    } else {
      logger.info('Starting bot polling...');
      await run(bot);
    }
  } catch (err) {
    logger.error('Bot encountered an error:', err);
    process.exit(1);
  }
}

// Start the bot
startBot().catch((err) => {
  logger.error('Failed to start bot:', err);
  process.exit(1);
});
