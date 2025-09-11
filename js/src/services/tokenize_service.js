import { config } from '../config.js';
import { dataBase, dbKey } from '../db/init_db.js';
import { asyncGet, asyncPost, asyncDelete, asyncPut } from './utils.js';
import { getUserName } from '../bot/utils.js';

class TokenizeService {
  constructor() {
    this.LAST_CHECK_DATE = 'last_check_date';
  }

  async getCheckDate(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, this.LAST_CHECK_DATE));
      return buf.toString('utf-8');
    } catch {
      return null;
    }
  }

  async setCheckDate(userId, value) {
    await dataBase.set(dbKey(userId, this.LAST_CHECK_DATE), value);
    await dataBase.commit();
  }

  async get_tokens(userId) {
    let tokens = await this.getUserTokens(userId);
    if (tokens) return tokens;
    await this.create_new_token(userId);
    return this.getUserTokens(userId);
  }

  async create_new_token(userId) {
    const payload = { masterToken: config.adminToken, userId: getUserName(userId) };
    const response = await asyncPost(`${config.proxyUrl}/token`, { params: payload, headers: { 'Content-Type': 'application/json' } });
    if (response.status === 200) return await response.json();
    return null;
  }

  async getUserTokens(userId) {
    const params = { masterToken: config.adminToken, userId: getUserName(userId) };
    const response = await asyncGet(`${config.proxyUrl}/token`, { params, headers: { 'Content-Type': 'application/json' } });
    if (response.status === 200) {
      const data = await response.json();
      if (data.id) return { ...data, tokens: data.tokens_gpt || 0 };
    }
    return null;
  }

  async update_user_token(userId, tokens, operation = 'add') {
    const params = { masterToken: config.adminToken, userId: getUserName(userId) };
    const payload = { operation, amount: tokens };
    const response = await asyncPut(`${config.proxyUrl}/token`, { params, json: payload, headers: { 'Content-Type': 'application/json' } });
    if (response.status === 200) return await response.json();
    return null;
  }

  async clear_dialog(userId) {
    const params = { masterToken: config.adminToken, userId: getUserName(userId) };
    const response = await asyncDelete(`${config.proxyUrl}/dialogs`, { params, headers: { 'Content-Type': 'application/json' } });
    if (response.status === 200) return await response.json();
    return null;
  }

  async history(userId) {
    const params = { masterToken: config.adminToken, dialogName: getUserName(userId) };
    const response = await asyncGet(`${config.proxyUrl}/dialog-history`, { params, headers: { 'Content-Type': 'application/json' } });
    if (response.status === 200) return { response: await response.json(), status: response.status };
    if (response.status === 404) return { status: 404 };
    return null;
  }

  async get_token(userId) {
    const params = { masterToken: config.adminToken, userId };
    const response = await asyncGet(`${config.proxyUrl}/token`, { params, headers: { 'Content-Type': 'application/json' } });
    if (response.status === 200) return await response.json();
    return null;
  }

  async regenerate_api_token(userId) {
    const params = { masterToken: config.adminToken, userId };
    const response = await asyncPost(`${config.proxyUrl}/token`, { params, headers: { 'Content-Type': 'application/json' } });
    if (response.status === 200) return await response.json();
    return null;
  }
}

export const tokenizeService = new TokenizeService();
