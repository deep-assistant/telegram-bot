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

// TODO: Port AlbumMiddleware to grammY if needed
// class AlbumMiddleware { ... }

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

  const bot = new Bot(config.TOKEN, {
    client: config.IS_DEV ? undefined : { baseUrl: config.ANALYTICS_URL }
  });

  // Set default parse_mode to MarkdownV2 for send* methods
  bot.api.config.use((prev, method, payload) => {
    if (method.startsWith('send') && !('parse_mode' in payload)) {
      return { ...payload, parse_mode: 'MarkdownV2' };
    }
    return payload;
  });

  bot.use(createI18nMiddleware());

  bot.catch((err) => {
    console.error('grammy error', err);
    process.exit(1);
  });

  applyRouters(bot);

  if (config.WEBHOOK_ENABLED) {
    debug('Starting via webhook');
    await bot.api.setWebhook(config.WEBHOOK_URL);
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
      await bot.api.deleteWebhook();
      process.exit(0);
    });
    process.on('SIGTERM', async () => {
      await onShutdown();
      await bot.api.deleteWebhook();
      process.exit(0);
    });

    // Keep process alive
    return new Promise(() => {});
  } else {
    debug('Starting polling');
    await bot.api.deleteWebhook({ drop_pending_updates: true });
    await bot.start();
  }
}
