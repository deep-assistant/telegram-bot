import { Bot as RealBot, InlineKeyboard as RealInlineKeyboard } from 'grammy';

export class Bot extends RealBot {
  constructor(options = {}) {
    super(options.token, options); // grammY expects (token, other)
    // Expose aiogram-like properties
    this.api = this.api || this.apiRaw || this; // fallback
    this.setWebhook = this.api.setWebhook?.bind(this.api) || (async () => {});
    this.deleteWebhook = this.api.deleteWebhook?.bind(this.api) || (async () => {});
  }
}

export class InlineKeyboard extends RealInlineKeyboard {}

export class Router {
  constructor() {
    this._handlers = [];
  }

  message(filterFn, handler) {
    this._handlers.push({ type: 'message', filter: filterFn, handler });
  }

  callbackQuery(filterFn, handler) {
    this._handlers.push({ type: 'callback', filter: filterFn, handler });
  }

  _bind(bot) {
    for (const h of this._handlers) {
      if (h.type === 'message') {
        bot.on('message:text', async (ctx) => {
          try {
            if (await h.filter(ctx.message)) await h.handler(ctx.message, {});
          } catch (e) { console.error(e); }
        });
      } else if (h.type === 'callback') {
        bot.on('callback_query:data', async (ctx) => {
          try {
            if (await h.filter({ data: ctx.callbackQuery.data })) await h.handler(ctx.callbackQuery, {});
          } catch (e) { console.error(e); }
        });
      }
    }
  }
} 