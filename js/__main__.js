import { startBot } from './index.js';
import { createLogger } from './utils/logger.js';

const log = createLogger('main');

if (import.meta.main) {
  log.info('Starting bot from __main__.js');
  startBot().catch((err) => {
    log.error('Failed to start bot:', () => err);
    process.exit(1);
  });
} 