import { Bot } from './grammy_stub.js';
// --- Original aiogram imports (commented out for reference) ---
// import { Bot as AiogramBot, Dispatcher as AiogramDispatcher, BaseMiddleware as AiogramBaseMiddleware } from 'aiogram';
// import { DefaultBotProperties as AiogramDefaultBotProperties } from 'aiogram/client/default.js';
// import { AiohttpSession as AiogramAiohttpSession } from 'aiogram/client/session/aiohttp.js';
// import { TelegramAPIServer as AiogramTelegramAPIServer } from 'aiogram/client/telegram.js';
// import { ParseMode as AiogramParseMode } from 'aiogram/enums.js';
// import { MemoryStorage as AiogramMemoryStorage } from 'aiogram/fsm/storage/memory.js';
// --------------------------------------------------------------
// Temporary stubs to keep existing aiogram-based code working during migration to grammY
class Dispatcher {
  constructor() {
    this.message = { use: () => {} };
    this.bot = {
      setWebhook: async () => {},
      deleteWebhook: async () => {},
    };
  }
  includeRouter() {}
  async startWebhook() {}
  async startPolling() {}
}
class BaseMiddleware {}

// Stubs for the above until they are fully migrated
const DefaultBotProperties = class { constructor(props) { this.props = props; } };
const AiohttpSession = class { constructor(opts) { this.opts = opts; } };
const TelegramAPIServer = class { static fromBase(url) { return { url }; } };
const ParseMode = { MARKDOWN: 'Markdown' };
const MemoryStorage = class {};

import config from '../config.js';
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

export function applyRouters(dp) {
  // dp.includeRouter(imagesRouter);
  // dp.includeRouter(sunoRouter);
  dp.includeRouter(startRouter);
  // dp.includeRouter(diagnosticsRouter);
  // dp.includeRouter(referralRouter);
  // dp.includeRouter(paymentsRouter);
  // dp.includeRouter(apiRouter);
  // dp.includeRouter(agreementRouter);
  // dp.includeRouter(imageEditingRouter);
  // dp.includeRouter(taskRouter);
  // dp.includeRouter(gptRouter);
}

class AlbumMiddleware extends BaseMiddleware {
  constructor() {
    super();
    this.albumData = {};
    this.batchData = {};
  }

  async __call__(handler, event, data) {
    // Batch first-handling or group-by-group
    if (!event.photo) {
      const dateKey = String(event.date);
      if (this.batchData[dateKey]) {
        this.batchData[dateKey].push(event);
        return;
      }
      this.batchData[dateKey] = [event];
      await new Promise(r => setTimeout(r, 10));
      event.model_config.is_last = true;
      data.batchMessages = this.batchData[dateKey];
      const result = await handler(event, data);
      if (event.model_config.is_last) delete this.batchData[dateKey];
      return result;
    }

    // Single/photo or grouped albums
    if (!event.media_group_id) {
      if (event.photo) data.album = [event];
      return handler(event, data);
    }

    if (this.albumData[event.media_group_id]) {
      this.albumData[event.media_group_id].push(event);
      return;
    }
    this.albumData[event.media_group_id] = [event];
    await new Promise(r => setTimeout(r, 10));
    event.model_config.is_last = true;
    data.album = this.albumData[event.media_group_id];
    const result = await handler(event, data);
    if (event.model_config.is_last) delete this.albumData[event.media_group_id];
    return result;
  }
}

async function onStartup(dp) {
  console.log('Bot is starting...');
  if (config.WEBHOOK_ENABLED) {
    await dp.bot.setWebhook(config.WEBHOOK_URL);
  }
}

async function onShutdown(dp) {
  console.log('Bot is shutting down...');
  if (config.WEBHOOK_ENABLED) {
    await dp.bot.deleteWebhook();
  }
}

export async function botRun() {
  const dp = new Dispatcher({ storage: new MemoryStorage() });
  dp.message.use(new AlbumMiddleware());
  applyRouters(dp);

  let bot;
  if (config.IS_DEV) {
    bot = new Bot({
      token: config.TOKEN,
      default: new DefaultBotProperties({ parse_mode: ParseMode.MARKDOWN })
    });
  } else {
    bot = new Bot({
      token: config.TOKEN,
      default: new DefaultBotProperties({ parse_mode: ParseMode.MARKDOWN }),
      session: new AiohttpSession({ api: TelegramAPIServer.fromBase(config.ANALYTICS_URL) })
    });
  }

  if (config.WEBHOOK_ENABLED) {
    await bot.setWebhook(config.WEBHOOK_URL);
    await dp.startWebhook({
      webhookPath: config.WEBHOOK_PATH,
      onStartup,
      onShutdown,
      host: config.WEBHOOK_HOST,
      port: config.WEBHOOK_PORT
    });
  } else {
    await bot.deleteWebhook();
    await dp.startPolling({ bot, skipUpdates: false, dropPendingUpdates: true });
  }
}
