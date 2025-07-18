import { Bot } from 'grammy';
import { run } from '@grammyjs/runner';
import { config } from './config.js';
import { startRouter } from './bot/start/router.js';
import { i18n } from './i18n.js';
import { createLogger } from './utils/logger.js';

const logger = createLogger('main');

// Enhanced AlbumMiddleware with batching (from bot_run.js)
function albumMiddleware() {
  const albumData = new Map();
  const batchData = new Map();

  return async (ctx, next) => {
    if (!ctx.message) return next();
    const msg = ctx.message;

    if (!msg.photo) {
      const dateKey = String(msg.date);
      if (!batchData.has(dateKey)) batchData.set(dateKey, []);
      batchData.get(dateKey).push(msg);

      // Wait briefly to collect batch
      await new Promise(r => setTimeout(r, 10));

      // Process only once for the batch
      if (batchData.get(dateKey)[batchData.get(dateKey).length - 1] === msg) {
        ctx.batchMessages = batchData.get(dateKey);
        await next();
        batchData.delete(dateKey);
      }
      return;
    }

    if (!msg.media_group_id) {
      if (msg.photo) ctx.album = [msg];
      return next();
    }

    const groupId = msg.media_group_id;
    if (!albumData.has(groupId)) albumData.set(groupId, []);
    albumData.get(groupId).push(msg);

    await new Promise(r => setTimeout(r, 10));

    if (albumData.get(groupId)[albumData.get(groupId).length - 1] === msg) {
      ctx.album = albumData.get(groupId);
      await next();
      albumData.delete(groupId);
    }
  };
}

async function onStartup() {
  logger.info('Bot is starting...');
}

async function onShutdown() {
  logger.info('Bot is shutting down...');
}

async function startBot() {
  logger.info('Starting bot...');
  
  const bot = new Bot(config.botToken);
  
  // Add middlewares
  bot.use(i18n);
  bot.use(albumMiddleware());
  
  // Add routers
  bot.use(startRouter);
  
  // Error handling
  bot.catch((err) => {
    logger.error('Bot error:', err);
    if (config.isDev) {
      logger.error('Development mode: Bot will exit due to error');
      process.exit(1);
    }
  });
  
  try {
    if (config.webhookEnabled && config.webhookUrl) {
      logger.info('Starting bot webhook...');
      
      // Delete existing webhook first
      try {
        await bot.api.deleteWebhook({ drop_pending_updates: true });
      } catch (err) {
        logger.warn('Failed to delete webhook:', err.message);
      }
      
      // Set new webhook
      try {
        await bot.api.setWebhook(config.webhookUrl);
      } catch (err) {
        logger.warn('Failed to set webhook:', err.message);
      }
      
      await onStartup();

      // Start webhook server
      Bun.serve({
        port: config.webhookPort,
        hostname: config.webhookHost,
        fetch(req) {
          const url = new URL(req.url);
          if (url.pathname === config.webhookPath && req.method === 'POST') {
            req.json().then(update => {
              bot.handleUpdate(update);
            });
            return new Response('OK', { status: 200 });
          }
          return new Response('Not Found', { status: 404 });
        },
      });

      // Handle shutdown
      process.on('SIGINT', async () => {
        await onShutdown();
        try {
          await bot.api.deleteWebhook();
        } catch (err) {
          logger.warn('Failed to delete webhook:', err.message);
        }
        process.exit(0);
      });
      process.on('SIGTERM', async () => {
        await onShutdown();
        try {
          await bot.api.deleteWebhook();
        } catch (err) {
          logger.warn('Failed to delete webhook:', err.message);
        }
        process.exit(0);
      });

      // Keep process alive
      return new Promise(() => {});
    } else {
      // Main mode: Long polling
      logger.info('Starting bot polling...');
      await onStartup();
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
