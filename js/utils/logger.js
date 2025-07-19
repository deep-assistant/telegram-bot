import pino from 'pino';

// Create log with lazy evaluation
const log = pino({
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

// Helper to add module prefix to log methods
const addModulePrefix = (log, module) => {
  const methods = ['debug', 'info', 'warn', 'error', 'trace'];
  methods.forEach(method => {
    const original = log[method].bind(log);
    log[method] = (...args) => {
      if (!log.isLevelEnabled(method)) return;
      
      // Convert all args to strings if they're functions
      const processedArgs = args.map(arg => {
        if (typeof arg === 'function') {
          return arg();
        }
        return arg;
      });
      
      original(`[${module}] ${processedArgs.join(' ')}`);
    };
  });
  return log;
};

// Create child logs for different modules with module prefix
export const createLogger = (module) => {
  const childLog = log.child({ module });
  return addModulePrefix(childLog, module);
};

// Export main log
export default log; 