import { dataBase, dbKey } from '../db/init_db.js';

class TimeEstimationService {
  static RESPONSE_TIMES_KEY = 'response_times';
  static AVERAGE_TIME_KEY = 'average_time';
  static MIN_TIME_KEY = 'min_time';
  static MAX_TIME_KEY = 'max_time';
  static REQUEST_COUNT_KEY = 'request_count';

  constructor() {
    // Maximum number of response times to store per user for calculation
    this.maxStoredTimes = 100;
  }

  /**
   * Record a response time for a user
   * @param {string|number} userId - User ID
   * @param {number} responseTime - Response time in milliseconds
   */
  async recordResponseTime(userId, responseTime) {
    if (typeof responseTime !== 'number' || responseTime <= 0) {
      return; // Invalid response time
    }

    try {
      // Get current response times
      const responseTimes = await this.getResponseTimes(userId);
      
      // Add new response time
      responseTimes.push(responseTime);
      
      // Keep only the most recent times (to prevent unlimited growth)
      if (responseTimes.length > this.maxStoredTimes) {
        responseTimes.shift(); // Remove oldest time
      }
      
      // Store updated response times
      await this.setResponseTimes(userId, responseTimes);
      
      // Update statistics
      await this.updateStatistics(userId, responseTimes);
      
      // Increment request count
      await this.incrementRequestCount(userId);
    } catch (error) {
      console.error('Error recording response time:', error);
    }
  }

  /**
   * Get stored response times for a user
   * @param {string|number} userId - User ID
   * @returns {Array<number>} Array of response times in milliseconds
   */
  async getResponseTimes(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, TimeEstimationService.RESPONSE_TIMES_KEY));
      if (buf) {
        return JSON.parse(buf.toString('utf-8'));
      }
    } catch (error) {
      console.error('Error getting response times:', error);
    }
    return [];
  }

  /**
   * Store response times for a user
   * @param {string|number} userId - User ID
   * @param {Array<number>} responseTimes - Array of response times
   */
  async setResponseTimes(userId, responseTimes) {
    await dataBase.set(dbKey(userId, TimeEstimationService.RESPONSE_TIMES_KEY), JSON.stringify(responseTimes));
  }

  /**
   * Update statistics (average, min, max) based on current response times
   * @param {string|number} userId - User ID
   * @param {Array<number>} responseTimes - Array of response times
   */
  async updateStatistics(userId, responseTimes) {
    if (responseTimes.length === 0) {
      return;
    }

    const sum = responseTimes.reduce((acc, time) => acc + time, 0);
    const average = sum / responseTimes.length;
    const min = Math.min(...responseTimes);
    const max = Math.max(...responseTimes);

    await Promise.all([
      dataBase.set(dbKey(userId, TimeEstimationService.AVERAGE_TIME_KEY), average.toString()),
      dataBase.set(dbKey(userId, TimeEstimationService.MIN_TIME_KEY), min.toString()),
      dataBase.set(dbKey(userId, TimeEstimationService.MAX_TIME_KEY), max.toString())
    ]);
  }

  /**
   * Get average response time for a user
   * @param {string|number} userId - User ID
   * @returns {number|null} Average response time in milliseconds, or null if no data
   */
  async getAverageTime(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, TimeEstimationService.AVERAGE_TIME_KEY));
      if (buf) {
        return parseFloat(buf.toString('utf-8'));
      }
    } catch (error) {
      console.error('Error getting average time:', error);
    }
    return null;
  }

  /**
   * Get minimum response time for a user
   * @param {string|number} userId - User ID
   * @returns {number|null} Minimum response time in milliseconds, or null if no data
   */
  async getMinTime(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, TimeEstimationService.MIN_TIME_KEY));
      if (buf) {
        return parseFloat(buf.toString('utf-8'));
      }
    } catch (error) {
      console.error('Error getting min time:', error);
    }
    return null;
  }

  /**
   * Get maximum response time for a user
   * @param {string|number} userId - User ID
   * @returns {number|null} Maximum response time in milliseconds, or null if no data
   */
  async getMaxTime(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, TimeEstimationService.MAX_TIME_KEY));
      if (buf) {
        return parseFloat(buf.toString('utf-8'));
      }
    } catch (error) {
      console.error('Error getting max time:', error);
    }
    return null;
  }

  /**
   * Get all time statistics for a user
   * @param {string|number} userId - User ID
   * @returns {Object} Object containing average, min, max times and request count
   */
  async getTimeStatistics(userId) {
    const [average, min, max, requestCount] = await Promise.all([
      this.getAverageTime(userId),
      this.getMinTime(userId),
      this.getMaxTime(userId),
      this.getRequestCount(userId)
    ]);

    return {
      average,
      min,
      max,
      requestCount
    };
  }

  /**
   * Increment the request count for a user
   * @param {string|number} userId - User ID
   */
  async incrementRequestCount(userId) {
    try {
      const currentCount = await this.getRequestCount(userId);
      await dataBase.set(dbKey(userId, TimeEstimationService.REQUEST_COUNT_KEY), (currentCount + 1).toString());
    } catch (error) {
      console.error('Error incrementing request count:', error);
    }
  }

  /**
   * Get the total request count for a user
   * @param {string|number} userId - User ID
   * @returns {number} Total number of requests made by the user
   */
  async getRequestCount(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, TimeEstimationService.REQUEST_COUNT_KEY));
      if (buf) {
        return parseInt(buf.toString('utf-8'), 10);
      }
    } catch (error) {
      console.error('Error getting request count:', error);
    }
    return 0;
  }

  /**
   * Format time in a human-readable way
   * @param {number} milliseconds - Time in milliseconds
   * @returns {string} Formatted time string
   */
  formatTime(milliseconds) {
    if (milliseconds < 1000) {
      return `${Math.round(milliseconds)}мс`;
    }
    
    const seconds = milliseconds / 1000;
    if (seconds < 60) {
      return `${seconds.toFixed(1)}с`;
    }
    
    const minutes = seconds / 60;
    if (minutes < 60) {
      return `${minutes.toFixed(1)}мин`;
    }
    
    const hours = minutes / 60;
    return `${hours.toFixed(1)}ч`;
  }

  /**
   * Get estimation message for user display
   * @param {string|number} userId - User ID
   * @returns {string} Formatted estimation message
   */
  async getEstimationMessage(userId) {
    const stats = await this.getTimeStatistics(userId);
    
    if (!stats.average || stats.requestCount === 0) {
      return '⏱️ Еще нет данных для оценки времени ответа';
    }

    const avgTime = this.formatTime(stats.average);
    const minTime = this.formatTime(stats.min);
    const maxTime = this.formatTime(stats.max);
    
    return `📊 **Статистика времени ответа:**\n` +
           `⚡️ Среднее время: **${avgTime}**\n` +
           `🚀 Минимальное: **${minTime}**\n` +
           `🐌 Максимальное: **${maxTime}**\n` +
           `📈 Всего запросов: **${stats.requestCount}**`;
  }
}

export const timeEstimationService = new TimeEstimationService();