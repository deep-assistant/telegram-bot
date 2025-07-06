import { Bot as RealBot, InlineKeyboard as RealInlineKeyboard } from 'grammy';
import createDebug from 'debug';
const rdebug = createDebug('telegram-bot:router');

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
    rdebug('Binding handlers to bot');
    for (const h of this._handlers) {
      if (h.type === 'message') {
        bot.on('message:text', async (ctx) => {
          rdebug('message:text', ctx.message.text);
          try {
            const msg = ctx.message;
            // Provide aiogram-like aliases and helpers
            msg.from_user = msg.from;
            msg.reply = (...args) => ctx.reply(...args);
            msg.answer = msg.reply;
            msg.message = msg; // so ctx.message.reply.bind(ctx.message) works
            if (await h.filter(msg)) await h.handler(msg, {});
          } catch (e) { console.error(e); }
        });
      } else if (h.type === 'callback') {
        bot.on('callback_query:data', async (ctx) => {
          rdebug('callback_query', ctx.callbackQuery.data);
          try {
            if (await h.filter({ data: ctx.callbackQuery.data })) await h.handler(ctx.callbackQuery, {});
          } catch (e) { console.error(e); }
        });
      }
    }
  }
} 