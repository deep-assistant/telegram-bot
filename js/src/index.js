import { Bot } from 'grammy';
import { run } from '@grammyjs/runner';
import { EventEmitter } from 'events';
import { config } from './config.js';
import { startRouter } from './bot/start/router.js';
// import agreementRouter from './bot/agreement/router.js';
// import apiRouter from './bot/api/router.js';
import { balanceRouter } from './bot/balance/router.js';
import { paymentRouter } from './bot/payment/router.js';
// import imageEditingRouter from './bot/image_editing/router.js';
// import imagesRouter from './bot/images/router.js';
// import referralRouter from './bot/referral/router.js';
// import sunoRouter from './bot/suno/router.js';
// import taskRouter from './bot/tasks/router.js';
// import diagnosticsRouter from './bot/diagnostics/router.js';
import { i18n } from './i18n.js';
import { createLogger } from './utils/logger.js';

const log = createLogger('main');

// Global shutdown emitter
export const shutdownEmitter = new EventEmitter();
let currentBot = null;
let currentRunner = null;

// Enhanced AlbumMiddleware with batching (from bot_run.js)
function albumMiddleware() {
  const albumData = new Map();
  const batchData = new Map();

  return async (ctx, next) => {
    if (!ctx.message) return next();
    const msg = ctx.message;

    if (!msg.photo) {
      const dateKey = String(msg.date);
      if (!batchData.has(dateKey)) batchData.set(dateKey, []);
      batchData.get(dateKey).push(msg);

      // Wait briefly to collect batch
      await new Promise(r => setTimeout(r, 10));

      // Process only once for the batch
      if (batchData.get(dateKey)[batchData.get(dateKey).length - 1] === msg) {
        ctx.batchMessages = batchData.get(dateKey);
        await next();
        batchData.delete(dateKey);
      }
      return;
    }

    if (!msg.media_group_id) {
      if (msg.photo) ctx.album = [msg];
      return next();
    }

    const groupId = msg.media_group_id;
    if (!albumData.has(groupId)) albumData.set(groupId, []);
    albumData.get(groupId).push(msg);

    await new Promise(r => setTimeout(r, 10));

    if (albumData.get(groupId)[albumData.get(groupId).length - 1] === msg) {
      ctx.album = albumData.get(groupId);
      await next();
      albumData.delete(groupId);
    }
  };
}

function applyRouters(bot) {
  log.debug('Applying routers');
  // bot.use(imagesRouter);
  // bot.use(sunoRouter);
  bot.use(startRouter);
  // bot.use(diagnosticsRouter);
  // bot.use(referralRouter);
  bot.use(paymentRouter);
  // bot.use(apiRouter);
  // bot.use(agreementRouter);
  // bot.use(imageEditingRouter);
  // bot.use(taskRouter);
  bot.use(balanceRouter);
}

async function onStartup() {
  log.info('Bot is starting...');
}

async function gracefulShutdown() {
  log.info('Bot is shutting down gracefully...');
  
  try {
    // Stop the runner if it exists (for polling mode)
    if (currentRunner) {
      log.info('Stopping bot runner...');
      await currentRunner.stop();
    }

    // Delete webhook if bot exists
    if (currentBot) {
      try {
        await currentBot.api.deleteWebhook();
        log.info('Webhook deleted successfully');
      } catch (err) {
        log.warn('Failed to delete webhook:', () => err.message);
      }
    }
    
    log.info('Bot shutdown completed');
  } catch (err) {
    log.error('Error during graceful shutdown:', () => err);
  }
  
  // Finally exit
  process.exit(0);
}

async function onShutdown() {
  log.info('Bot is shutting down...');
}

async function startBot() {
  log.info('Starting bot...');
  
  // Initialize the bot based on the development flag (mirroring Python logic)
  if (config.isDev) {
    currentBot = new Bot(config.botToken);
  } else {
    // Production mode with analytics URL
    currentBot = new Bot(config.botToken, {
      // Note: grammY doesn't have direct session configuration like aiogram
      // We'll handle analytics through API calls when needed
    });
  }
  
  // Set up shutdown listener
  shutdownEmitter.once('shutdown', gracefulShutdown);
  
  // Add middlewares
  currentBot.use(i18n);
  currentBot.use(albumMiddleware());
  
  // Apply routers
  applyRouters(currentBot);
  
  // Error handling
  currentBot.catch((err) => {
    log.error('Bot error:', () => err);
    if (config.isDev) {
      log.error('Development mode: Bot will exit due to error');
      process.exit(1);
    }
  });
  
  try {
    if (config.webhookEnabled && config.webhookUrl) {
      log.info('Starting bot webhook...');
      
      // Delete existing webhook first
      try {
        await currentBot.api.deleteWebhook({ drop_pending_updates: true });
      } catch (err) {
        log.warn('Failed to delete webhook:', () => err.message);
      }
      
      // Set new webhook with enhanced options
      try {
        const webhookOptions = {
          url: config.webhookUrl,
          drop_pending_updates: true,
          max_connections: config.webhookMaxConnections
        };
        
        // Add secret token if configured
        if (config.webhookSecretToken) {
          webhookOptions.secret_token = config.webhookSecretToken;
        }
        
        await currentBot.api.setWebhook(webhookOptions);
        log.info(`Webhook configured with max_connections: ${config.webhookMaxConnections}`);
      } catch (err) {
        log.warn('Failed to set webhook:', () => err.message);
      }
      
      await onStartup();

      // Start enhanced webhook server with performance optimizations
      const server = Bun.serve({
        port: config.webhookPort,
        hostname: config.webhookHost,
        
        // Enhanced request handler with security and monitoring
        async fetch(req) {
          const url = new URL(req.url);
          const startTime = Date.now();
          
          try {
            // Health check endpoint
            if (url.pathname === '/health' && req.method === 'GET') {
              return new Response(JSON.stringify({
                status: 'healthy',
                timestamp: Date.now(),
                webhook_url: config.webhookUrl
              }), {
                headers: { 'Content-Type': 'application/json' },
                status: 200
              });
            }
            
            // Webhook handler with optimizations
            if (url.pathname === config.webhookPath && req.method === 'POST') {
              // Validate content type
              const contentType = req.headers.get('content-type');
              if (!contentType || !contentType.includes('application/json')) {
                log.warn('Invalid content type for webhook request');
                return new Response('Bad Request', { status: 400 });
              }
              
              // Validate secret token if configured
              if (config.webhookSecretToken) {
                const secretHeader = req.headers.get('x-telegram-bot-api-secret-token');
                if (secretHeader !== config.webhookSecretToken) {
                  log.warn('Invalid webhook secret token');
                  return new Response('Unauthorized', { status: 401 });
                }
              }
              
              // Parse and handle update with error handling
              try {
                const update = await req.json();
                
                // Handle update asynchronously for better throughput
                setImmediate(() => {
                  currentBot.handleUpdate(update).catch(err => {
                    log.error('Error handling update:', () => err);
                  });
                });
                
                const responseTime = Date.now() - startTime;
                log.debug(`Webhook request processed in ${responseTime}ms`);
                
                return new Response('OK', { 
                  status: 200,
                  headers: {
                    'Content-Type': 'text/plain',
                    'X-Response-Time': `${responseTime}ms`
                  }
                });
              } catch (err) {
                log.error('Error parsing webhook JSON:', () => err);
                return new Response('Bad Request', { status: 400 });
              }
            }
            
            return new Response('Not Found', { status: 404 });
          } catch (err) {
            log.error('Webhook server error:', () => err);
            return new Response('Internal Server Error', { status: 500 });
          }
        },
        
        // Enable better performance options
        development: config.isDev,
      });
      
      log.info(`Enhanced webhook server started on ${config.webhookHost}:${config.webhookPort}`);
      log.info(`Webhook URL: ${config.webhookUrl}`);
      log.info(`Health check: http://${config.webhookHost}:${config.webhookPort}/health`);

      // Handle shutdown
      process.on('SIGINT', gracefulShutdown);
      process.on('SIGTERM', gracefulShutdown);

      // Keep process alive
      return new Promise(() => {});
    } else {
      // Main mode: Long polling (mirroring Python logic)
      log.info('Starting bot polling...');
      
      // Delete webhook if exists (mirroring Python logic)
      try {
        await currentBot.api.deleteWebhook({ drop_pending_updates: true });
      } catch (err) {
        log.warn('Failed to delete webhook:', () => err.message);
      }
      
      await onStartup();
      
      // Handle shutdown for polling mode
      process.on('SIGINT', gracefulShutdown);
      process.on('SIGTERM', gracefulShutdown);
      
      // Start polling with options (mirroring Python skip_updates=False, drop_pending_updates=True)
      currentRunner = run(currentBot, {
        runner: {
          drop_pending_updates: true
        }
      });
      
      await currentRunner;
    }
  } catch (err) {
    log.error('Bot encountered an error:', () => err);
    process.exit(1);
  }
}

// Export startBot for use in __main__.js
export { startBot };

// Start the bot if this file is run directly
if (import.meta.main) {
  startBot().catch((err) => {
    log.error('Failed to start bot:', () => err);
    process.exit(1);
  });
}
