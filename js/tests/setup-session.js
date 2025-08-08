import { setupOrCheckSession } from './user-bot.js';

if (import.meta.main) {
  setupOrCheckSession().catch(console.error);
}