import config from '../config.js';
import { asyncGet, asyncPost } from './utils.js';

class ReferralsService {
  async getAwards(userId) {
    const params = { masterToken: config.ADMIN_TOKEN, userId };
    const response = await asyncGet(`${config.PROXY_URL}/referral/award`, { params });
    return response.json();
  }

  async createReferral(userId, referralId = null) {
    const params = { masterToken: config.ADMIN_TOKEN, userId, referralId };
    const response = await asyncPost(`${config.PROXY_URL}/referral`, { params });
    if (response.status === 400) return null;
    return response.json();
  }

  async getReferral(userId) {
    const params = { masterToken: config.ADMIN_TOKEN, userId };
    const response = await asyncGet(`${config.PROXY_URL}/referral`, { params });
    return response.json();
  }
}

export const referralsService = new ReferralsService();
