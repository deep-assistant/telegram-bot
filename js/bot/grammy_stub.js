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