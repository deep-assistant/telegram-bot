import { config } from '../config.js';
import { asyncGet, asyncPost } from './utils.js';

class SystemMessageService {
  async getSystemMessage(userId) {
    const params = { masterToken: config.adminToken, userId };
const response = await asyncGet(`${config.proxyUrl}/system-message`, { params });
    return response.json();
  }

  async editSystemMessage(userId, message) {
    const params = { masterToken: config.adminToken };
const payload = { userId, message };
const response = await asyncPost(`${config.proxyUrl}/system-message`, { params, json: payload });
    return response.json();
  }
}

export const systemMessage = new SystemMessageService();
