import { Bot } from 'grammy';
import { run } from '@grammyjs/runner';
import { config } from './config.js';
import { startRouter } from './bot/start/router.js';
// import agreementRouter from './bot/agreement/router.js';
// import apiRouter from './bot/api/router.js';
import { balanceRouter } from './bot/balance/router.js';
import { paymentRouter } from './bot/payment/router.js';
// import imageEditingRouter from './bot/image_editing/router.js';
// import imagesRouter from './bot/images/router.js';
// import referralRouter from './bot/referral/router.js';
// import sunoRouter from './bot/suno/router.js';
// import taskRouter from './bot/tasks/router.js';
// import diagnosticsRouter from './bot/diagnostics/router.js';
import { i18n } from './i18n.js';
import { createLogger } from './utils/logger.js';

const log = createLogger('main');

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

function applyRouters(bot) {
  log.debug('Applying routers');
  // bot.use(imagesRouter);
  // bot.use(sunoRouter);
  bot.use(startRouter);
  // bot.use(diagnosticsRouter);
  // bot.use(referralRouter);
  bot.use(paymentRouter);
  // bot.use(apiRouter);
  // bot.use(agreementRouter);
  // bot.use(imageEditingRouter);
  // bot.use(taskRouter);
  bot.use(balanceRouter);
}

async function onStartup() {
  log.info('Bot is starting...');
}

async function onShutdown() {
  log.info('Bot is shutting down...');
}

async function startBot() {
  log.info('Starting bot...');
  
  // Initialize the bot based on the development flag (mirroring Python logic)
  let bot;
  if (config.isDev) {
    bot = new Bot(config.botToken);
  } else {
    // Production mode with analytics URL
    bot = new Bot(config.botToken, {
      // Note: grammY doesn't have direct session configuration like aiogram
      // We'll handle analytics through API calls when needed
    });
  }
  
  // Add middlewares
  bot.use(i18n);
  bot.use(albumMiddleware());
  
  // Apply routers
  applyRouters(bot);
  
  // Error handling
  bot.catch((err) => {
    log.error('Bot error:', () => err);
    if (config.isDev) {
      log.error('Development mode: Bot will exit due to error');
      process.exit(1);
    }
  });
  
  try {
    if (config.webhookEnabled && config.webhookUrl) {
      log.info('Starting bot webhook...');
      
      // Delete existing webhook first
      try {
        await bot.api.deleteWebhook({ drop_pending_updates: true });
      } catch (err) {
        log.warn('Failed to delete webhook:', () => err.message);
      }
      
      // Set new webhook
      try {
        await bot.api.setWebhook(config.webhookUrl);
      } catch (err) {
        log.warn('Failed to set webhook:', () => err.message);
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
          log.warn('Failed to delete webhook:', () => err.message);
        }
        process.exit(0);
      });
      process.on('SIGTERM', async () => {
        await onShutdown();
        try {
          await bot.api.deleteWebhook();
        } catch (err) {
          log.warn('Failed to delete webhook:', () => err.message);
        }
        process.exit(0);
      });

      // Keep process alive
      return new Promise(() => {});
    } else {
      // Main mode: Long polling (mirroring Python logic)
      log.info('Starting bot polling...');
      
      // Delete webhook if exists (mirroring Python logic)
      try {
        await bot.api.deleteWebhook({ drop_pending_updates: true });
      } catch (err) {
        log.warn('Failed to delete webhook:', () => err.message);
      }
      
      await onStartup();
      
      // Start polling with options (mirroring Python skip_updates=False, drop_pending_updates=True)
      await run(bot, {
        runner: {
          drop_pending_updates: true
        }
      });
    }
  } catch (err) {
    log.error('Bot encountered an error:', () => err);
    process.exit(1);
  }
}

// Export startBot for use in __main__.js
export { startBot };

// Start the bot if this file is run directly
if (import.meta.main) {
  startBot().catch((err) => {
    log.error('Failed to start bot:', () => err);
    process.exit(1);
  });
}
