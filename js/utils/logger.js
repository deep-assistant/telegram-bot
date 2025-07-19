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

// Create child loggers for different modules with module prefix
export const createLogger = (module) => {
  const childLogger = logger.child({ module });
  
  // Override log methods to include module prefix
  const originalDebug = childLogger.debug.bind(childLogger);
  const originalInfo = childLogger.info.bind(childLogger);
  const originalWarn = childLogger.warn.bind(childLogger);
  const originalError = childLogger.error.bind(childLogger);
  const originalTrace = childLogger.trace.bind(childLogger);
  
  childLogger.debug = (msg, ...args) => originalDebug(`[${module}] ${msg}`, ...args);
  childLogger.info = (msg, ...args) => originalInfo(`[${module}] ${msg}`, ...args);
  childLogger.warn = (msg, ...args) => originalWarn(`[${module}] ${msg}`, ...args);
  childLogger.error = (msg, ...args) => originalError(`[${module}] ${msg}`, ...args);
  childLogger.trace = (msg, ...args) => originalTrace(`[${module}] ${msg}`, ...args);
  
  return childLogger;
};

// Export main logger
export default logger;

// Enhanced lazy evaluation helpers with better debugging
export const lazyDebug = (logger, fn) => {
  if (logger.isLevelEnabled('debug')) {
    return fn();
  }
  return undefined;
};

export const lazyTrace = (logger, fn) => {
  if (logger.isLevelEnabled('trace')) {
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

// Special debugging helpers for complex objects
export const debugObject = (logger, label, obj) => {
  if (logger.isLevelEnabled('debug')) {
    try {
      const serialized = JSON.stringify(obj, null, 2);
      logger.debug(`${label}: ${serialized}`);
    } catch (error) {
      logger.debug(`${label}: [Object cannot be serialized]`);
    }
  }
};

export const traceObject = (logger, label, obj) => {
  if (logger.isLevelEnabled('trace')) {
    try {
      const serialized = JSON.stringify(obj, null, 2);
      logger.trace(`${label}: ${serialized}`);
    } catch (error) {
      logger.trace(`${label}: [Object cannot be serialized]`);
    }
  }
};

// Helper for callback data debugging
export const debugCallback = (logger, label, callbackData) => {
  if (logger.isLevelEnabled('debug')) {
    logger.debug(`${label}: ${callbackData}`);
  }
};

// Helper for keyboard debugging
export const debugKeyboard = (logger, label, keyboard) => {
  if (logger.isLevelEnabled('debug')) {
    try {
      const serialized = JSON.stringify(keyboard, null, 2);
      logger.debug(`${label}: ${serialized}`);
    } catch (error) {
      logger.debug(`${label}: [Keyboard cannot be serialized]`);
    }
  }
}; 