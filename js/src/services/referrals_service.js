import { config } from '../config.js';
import { asyncGet, asyncPost } from './utils.js';

class ReferralsService {
  async getAwards(userId) {
    const params = { masterToken: config.adminToken, userId };
const response = await asyncGet(`${config.proxyUrl}/referral/award`, { params });
    return response.json();
  }

  async createReferral(userId, referralId = null) {
    const params = { masterToken: config.adminToken, userId, referralId };
const response = await asyncPost(`${config.proxyUrl}/referral`, { params });
    if (response.status === 400) return null;
    return response.json();
  }

  async getReferral(userId) {
    const params = { masterToken: config.adminToken, userId };
const response = await asyncGet(`${config.proxyUrl}/referral`, { params });
    return response.json();
  }
}

export const referralsService = new ReferralsService();
