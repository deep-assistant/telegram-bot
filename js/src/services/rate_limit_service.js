import { dataBase, dbKey } from '../db/init_db.js';
import { createLogger } from '../utils/logger.js';
import { tokenizeService } from './tokenize_service.js';
import { config } from '../config.js';

const log = createLogger('rate_limit_service');

/**
 * Rate limiting service that tracks user requests per minute
 * Supports configurable limits based on user energy/subscription level
 */
class RateLimitService {
  constructor() {
    // Rate limits from configuration
    this.DEFAULT_REQUESTS_PER_MINUTE = config.defaultRequestsPerMinute;
    this.PREMIUM_REQUESTS_PER_MINUTE = config.premiumRequestsPerMinute;
    this.PREMIUM_ENERGY_THRESHOLD = config.premiumEnergyThreshold;
    
    // Redis/DB keys
    this.RATE_LIMIT_KEY = 'rate_limit';
    this.RATE_LIMIT_RESET_KEY = 'rate_limit_reset';
  }

  /**
   * Get the current rate limit for a user based on their energy
   * @param {number} userId - Telegram user ID
   * @returns {Promise<number>} - Requests per minute allowed
   */
  async getUserRateLimit(userId) {
    try {
      // Get user's energy/tokens to determine their limit
      const userTokens = await tokenizeService.get_tokens(userId);
      const energy = userTokens?.tokens || 0;
      
      // Users with high energy get premium limits
      if (energy >= this.PREMIUM_ENERGY_THRESHOLD) {
        log.debug(`User ${userId} has premium rate limit (${energy} energy)`);
        return this.PREMIUM_REQUESTS_PER_MINUTE;
      }
      
      log.debug(`User ${userId} has default rate limit (${energy} energy)`);
      return this.DEFAULT_REQUESTS_PER_MINUTE;
    } catch (error) {
      log.error('Error getting user rate limit:', () => error);
      return this.DEFAULT_REQUESTS_PER_MINUTE;
    }
  }

  /**
   * Get current request count for a user in the current minute
   * @param {number} userId - Telegram user ID
   * @returns {Promise<{count: number, resetTime: number}>}
   */
  async getCurrentCount(userId) {
    try {
      const currentMinute = Math.floor(Date.now() / 60000); // Current minute timestamp
      
      // Get stored reset time and count
      const resetTimeBuf = await dataBase.get(dbKey(userId, this.RATE_LIMIT_RESET_KEY));
      const countBuf = await dataBase.get(dbKey(userId, this.RATE_LIMIT_KEY));
      
      const storedResetTime = resetTimeBuf ? parseInt(resetTimeBuf.toString('utf-8'), 10) : 0;
      const storedCount = countBuf ? parseInt(countBuf.toString('utf-8'), 10) : 0;
      
      // If we're in a new minute, reset the counter
      if (currentMinute > storedResetTime) {
        await this.resetUserCount(userId, currentMinute);
        return { count: 0, resetTime: currentMinute };
      }
      
      return { count: storedCount, resetTime: storedResetTime };
    } catch (error) {
      log.error('Error getting current count:', () => error);
      return { count: 0, resetTime: Math.floor(Date.now() / 60000) };
    }
  }

  /**
   * Reset user's request count for a new minute
   * @param {number} userId - Telegram user ID
   * @param {number} currentMinute - Current minute timestamp
   */
  async resetUserCount(userId, currentMinute) {
    try {
      await dataBase.set(dbKey(userId, this.RATE_LIMIT_KEY), '0');
      await dataBase.set(dbKey(userId, this.RATE_LIMIT_RESET_KEY), currentMinute.toString());
      await dataBase.commit();
    } catch (error) {
      log.error('Error resetting user count:', () => error);
    }
  }

  /**
   * Increment user's request count
   * @param {number} userId - Telegram user ID
   * @returns {Promise<number>} - New count
   */
  async incrementCount(userId) {
    try {
      const { count } = await this.getCurrentCount(userId);
      const newCount = count + 1;
      
      await dataBase.set(dbKey(userId, this.RATE_LIMIT_KEY), newCount.toString());
      await dataBase.commit();
      
      return newCount;
    } catch (error) {
      log.error('Error incrementing count:', () => error);
      return 1;
    }
  }

  /**
   * Check if a user is within their rate limit
   * @param {number} userId - Telegram user ID
   * @returns {Promise<{allowed: boolean, limit: number, current: number, resetIn: number}>}
   */
  async checkRateLimit(userId) {
    try {
      const limit = await this.getUserRateLimit(userId);
      const { count, resetTime } = await this.getCurrentCount(userId);
      
      const currentMinute = Math.floor(Date.now() / 60000);
      const resetIn = Math.max(0, (resetTime + 1) * 60000 - Date.now()); // Milliseconds until reset
      
      const allowed = count < limit;
      
      log.debug(`Rate limit check for user ${userId}: ${count}/${limit}, reset in ${resetIn}ms`);
      
      return {
        allowed,
        limit,
        current: count,
        resetIn
      };
    } catch (error) {
      log.error('Error checking rate limit:', () => error);
      // On error, allow the request but with default limits
      return {
        allowed: true,
        limit: this.DEFAULT_REQUESTS_PER_MINUTE,
        current: 0,
        resetIn: 60000
      };
    }
  }

  /**
   * Process a request and update rate limiting counters
   * @param {number} userId - Telegram user ID
   * @returns {Promise<{allowed: boolean, limit: number, current: number, resetIn: number}>}
   */
  async processRequest(userId) {
    try {
      const rateCheck = await this.checkRateLimit(userId);
      
      if (rateCheck.allowed) {
        // Increment the counter
        const newCount = await this.incrementCount(userId);
        return {
          ...rateCheck,
          current: newCount
        };
      }
      
      return rateCheck;
    } catch (error) {
      log.error('Error processing request:', () => error);
      return {
        allowed: true,
        limit: this.DEFAULT_REQUESTS_PER_MINUTE,
        current: 1,
        resetIn: 60000
      };
    }
  }

  /**
   * Get rate limit status for a user (for debugging/admin purposes)
   * @param {number} userId - Telegram user ID
   * @returns {Promise<object>}
   */
  async getStatus(userId) {
    try {
      const rateCheck = await this.checkRateLimit(userId);
      const userTokens = await tokenizeService.get_tokens(userId);
      
      return {
        userId,
        energy: userTokens?.tokens || 0,
        isPremium: (userTokens?.tokens || 0) >= this.PREMIUM_ENERGY_THRESHOLD,
        ...rateCheck
      };
    } catch (error) {
      log.error('Error getting status:', () => error);
      return {
        userId,
        energy: 0,
        isPremium: false,
        allowed: true,
        limit: this.DEFAULT_REQUESTS_PER_MINUTE,
        current: 0,
        resetIn: 60000
      };
    }
  }
}

export const rateLimitService = new RateLimitService();