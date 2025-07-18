import { startBot } from './index.js';
import { createLogger } from './utils/logger.js';

const logger = createLogger('main');

if (import.meta.main) {
  logger.info('Starting bot from __main__.js');
  startBot().catch((err) => {
    logger.error('Failed to start bot:', err);
    process.exit(1);
  });
} 