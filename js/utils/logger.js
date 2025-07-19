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
          translateTime: 'yyyy-mm-dd HH:MM:ss.l',
          ignore: 'pid,hostname,module',
          hideObject: false,
          singleLine: false
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

// Helper to add module prefix to logger methods
const addModulePrefix = (logger, module) => {
  const methods = ['debug', 'info', 'warn', 'error', 'trace'];
  methods.forEach(method => {
    const original = logger[method].bind(logger);
    logger[method] = (msg, ...args) => original(`[${module}] ${msg}`, ...args);
  });
  return logger;
};

// Create child loggers for different modules with module prefix
export const createLogger = (module) => {
  const childLogger = logger.child({ module });
  return addModulePrefix(childLogger, module);
};

// Export main logger
export default logger;

// Lazy evaluation helpers
export const lazyDebug = (logger, fn) => logger.isLevelEnabled('debug') ? fn() : undefined;
export const lazyTrace = (logger, fn) => logger.isLevelEnabled('trace') ? fn() : undefined;
export const lazyInfo = (logger, fn) => logger.isLevelEnabled('info') ? fn() : undefined;
export const lazyWarn = (logger, fn) => logger.isLevelEnabled('warn') ? fn() : undefined;
export const lazyError = (logger, fn) => logger.isLevelEnabled('error') ? fn() : undefined;

// Debugging helpers
export const debugObject = (logger, label, obj) => {
  if (logger.isLevelEnabled('debug')) {
    try {
      logger.debug(`${label}: ${JSON.stringify(obj, null, 2)}`);
    } catch (error) {
      logger.debug(`${label}: [Object cannot be serialized]`);
    }
  }
};

export const traceObject = (logger, label, obj) => {
  if (logger.isLevelEnabled('trace')) {
    try {
      logger.trace(`${label}: ${JSON.stringify(obj, null, 2)}`);
    } catch (error) {
      logger.trace(`${label}: [Object cannot be serialized]`);
    }
  }
};

export const debugCallback = (logger, label, callbackData) => {
  if (logger.isLevelEnabled('debug')) {
    logger.debug(`${label}: ${callbackData}`);
  }
};

export const debugKeyboard = (logger, label, keyboard) => {
  if (logger.isLevelEnabled('debug')) {
    try {
      logger.debug(`${label}: ${JSON.stringify(keyboard, null, 2)}`);
    } catch (error) {
      logger.debug(`${label}: [Keyboard cannot be serialized]`);
    }
  }
}; 