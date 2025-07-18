import pino from 'pino';

// Create logger with lazy evaluation
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    targets: [
      // Console output
      {
        target: 'pino-pretty',
        level: process.env.LOG_LEVEL || 'info',
        options: {
          colorize: true,
          translateTime: 'SYS:standard',
          ignore: 'pid,hostname',
        }
      },
      // File output
      {
        target: 'pino/file',
        level: process.env.LOG_LEVEL || 'info',
        options: {
          destination: './logs/bot.log',
          mkdir: true
        }
      }
    ]
  }
});

// Create child loggers for different modules
export const createLogger = (module) => {
  return logger.child({ module });
};

// Export main logger
export default logger;

// Lazy evaluation helpers
export const lazyDebug = (logger, fn) => {
  if (logger.isLevelEnabled('debug')) {
    return fn();
  }
  return undefined;
};

export const lazyInfo = (logger, fn) => {
  if (logger.isLevelEnabled('info')) {
    return fn();
  }
  return undefined;
};

export const lazyWarn = (logger, fn) => {
  if (logger.isLevelEnabled('warn')) {
    return fn();
  }
  return undefined;
};

export const lazyError = (logger, fn) => {
  if (logger.isLevelEnabled('error')) {
    return fn();
  }
  return undefined;
}; 