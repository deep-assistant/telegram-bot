import config from '../config.js';
import { getUserName } from '../bot/utils.js';
import { asyncPost } from './utils.js';

class CompletionsService {
  constructor() {
    this.history = {};
  }

  clearHistory(userId) {
    this.history[userId] = [];
  }

  getHistory(userId) {
    if (!this.history[userId]) this.history[userId] = [];
    return this.history[userId];
  }

  updateHistory(userId, item) {
    this.getHistory(userId).push(item);
  }

  cutHistory(userId) {
    // TODO: implement trimming logic
  }

  async query_chatgpt(userId, message, systemMessage, gptModel, botModel, singleMessage) {
    const params = { masterToken: config.ADMIN_TOKEN };
    const payload = {
      userId: getUserName(userId),
      content: message,
      systemMessage,
      model: gptModel
    };
    const response = await asyncPost(`${config.PROXY_URL}/completions`, { json: payload, params });
    // TODO: parse OpenAI-like response, return { success, response, model }
    try {
      const data = await response.json();
      return { success: true, response: data.choices?.[0]?.message?.content ?? '', model: data.model };
    } catch {
      return { success: false, response: 'Error fetching completion' };
    }
  }
}

export const completionsService = new CompletionsService();
