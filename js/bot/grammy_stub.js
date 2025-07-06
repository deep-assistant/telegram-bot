export class Bot {
  constructor(options = {}) {
    this.options = options;
    this.api = {
      sendMessage: async () => {},
      setWebhook: async () => {},
      deleteWebhook: async () => {},
    };
    // Expose convenience methods
    this.setWebhook = this.api.setWebhook;
    this.deleteWebhook = this.api.deleteWebhook;
  }
}

export class InlineKeyboard {
  constructor(buttons = []) {
    this.buttons = buttons;
  }
  // chaining helpers for compatibility
  text() { return this; }
  url() { return this; }
  row() { return this; }
} 