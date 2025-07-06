import path from 'path';
// --- Original Vedis import kept for reference ---
// import { Vedis } from 'vedis';

// Switching to Redis (ioredis) as the underlying KV store
import Redis from 'ioredis';

const redisUrl = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const redisClient = new Redis(redisUrl);

// Provide a thin wrapper exposing the interface expected by the rest of the code
const dataBase = {
  async get(key) {
    // ioredis getBuffer returns Buffer|null
    return await redisClient.getBuffer(key);
  },
  async set(key, value) {
    // Accept Buffer or string
    await redisClient.set(key, value);
  },
  async commit() {
    // Vedis required commit; Redis writes immediately, so this is a no-op for compatibility
    return Promise.resolve();
  }
};

export function dbKey(userId, key) {
  return `${userId}_${key}`;
}

export { dataBase };
