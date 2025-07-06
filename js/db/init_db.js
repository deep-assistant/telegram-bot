import path from 'path';
// --- Original Vedis import kept for reference ---
// import { Vedis } from 'vedis';

// Switching to Redis (ioredis) as the underlying KV store
import Redis from 'ioredis';

const redisUrl = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
let redisClient;
try {
  redisClient = new Redis(redisUrl);
  // If the connection fails later, we'll fall back automatically.
} catch {
  // Ignore constructor errors – will use in-memory map.
  redisClient = null;
}

// In-memory fallback store (used if Redis is not connected or errors out)
const kv = new Map();

function redisReady() {
  return redisClient && ['ready', 'connect'].includes(redisClient.status);
}

// Provide a thin wrapper exposing the interface expected by the rest of the code
const dataBase = {
  async get(key) {
    if (redisReady()) {
      try {
        // ioredis getBuffer returns Buffer|null
        return await redisClient.getBuffer(key);
      } catch {}
    }
    return kv.has(key) ? kv.get(key) : null;
  },
  async set(key, value) {
    if (redisReady()) {
      try {
        // Accept Buffer or string
        await redisClient.set(key, value);
        return;
      } catch {}
    }
    kv.set(key, value);
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
