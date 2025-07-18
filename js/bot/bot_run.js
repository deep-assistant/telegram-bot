import { Bot } from 'grammy';
import path from 'path';
import { fileURLToPath } from 'url';
import { createI18nMiddleware } from '../i18n.js';
import createDebug from 'debug';
const debug = createDebug('telegram-bot:bot_run');

// import agreementRouter from './agreement/router.js';
// import apiRouter from './api/router.js';
// import gptRouter from './gpt/router.js';
// import imageEditingRouter from './image_editing/router.js';
// import imagesRouter from './images/router.js';
// import paymentsRouter from './payment/router.js';
// import referralRouter from './referral/router.js';
import { startRouter } from './start/router.js';
// import sunoRouter from './suno/router.js';
// import taskRouter from './tasks/router.js';
// import diagnosticsRouter from './diagnostics/router.js';

import config from '../config.js';

export function applyRouters(bot) {
  debug('Applying routers');
  // bot.use(imagesRouter);
  // bot.use(sunoRouter);
  bot.use(startRouter);
  // bot.use(diagnosticsRouter);
  // bot.use(referralRouter);
  // bot.use(paymentsRouter);
  // bot.use(apiRouter);
  // bot.use(agreementRouter);
  // bot.use(imageEditingRouter);
  // bot.use(taskRouter);
  // bot.use(gptRouter);
}

// Ported AlbumMiddleware to grammY
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
  debug('onStartup');
  console.log('Bot is starting...');
}

async function onShutdown() {
  debug('onShutdown');
  console.log('Bot is shutting down...');
}

export async function botRun() {
  debug('botRun start');

  const bot = new Bot(config.TOKEN);

  // Note: API configuration was causing issues, so we'll handle parse_mode in individual calls
  // bot.api.config.use((prev, method, payload) => {
  //   if (method.startsWith('send') && !('parse_mode' in payload)) {
  //     return { ...payload, parse_mode: 'MarkdownV2' };
  //   }
  //   return payload;
  // });

  bot.use(createI18nMiddleware());
  bot.use(albumMiddleware());

  bot.catch((err) => {
    console.error('grammy error', err);
    process.exit(1);
  });

  applyRouters(bot);

  if (config.WEBHOOK_ENABLED) {
    debug('Starting via webhook');
    try {
      await bot.api.setWebhook(config.WEBHOOK_URL);
    } catch (err) {
      console.warn('Failed to set webhook:', err.message);
    }
    await onStartup();

    Bun.serve({
      port: config.WEBHOOK_PORT,
      hostname: config.WEBHOOK_HOST,
      fetch(req) {
        const url = new URL(req.url);
        if (url.pathname === config.WEBHOOK_PATH && req.method === 'POST') {
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
        console.warn('Failed to delete webhook:', err.message);
      }
      process.exit(0);
    });
    process.on('SIGTERM', async () => {
      await onShutdown();
      try {
        await bot.api.deleteWebhook();
      } catch (err) {
        console.warn('Failed to delete webhook:', err.message);
      }
      process.exit(0);
    });

    // Keep process alive
    return new Promise(() => {});
  } else {
    debug('Starting polling');
    try {
      await bot.api.deleteWebhook({ drop_pending_updates: true });
    } catch (err) {
      console.warn('Failed to delete webhook:', err.message);
    }
    try {
      console.log('Starting bot polling...');
      await bot.start();
    } catch (err) {
      console.error('Failed to start bot:', err.message);
      console.error('Full error:', err);
      process.exit(1);
    }
  }
}
