import { rateLimitService } from '../services/index.js';
import { createLogger } from '../utils/logger.js';
import { config } from '../config.js';

const log = createLogger('rate_limit_middleware');

/**
 * Rate limiting middleware for Grammy bot
 * Checks if user has exceeded their rate limit before processing messages
 */
export function rateLimitMiddleware() {
  return async (ctx, next) => {
    // Skip rate limiting if disabled in config
    if (!config.rateLimitEnabled) {
      return next();
    }

    // Skip rate limiting for certain commands that shouldn't count
    const exemptCommands = ['/start', '/help', '/balance'];
    const messageText = ctx.message?.text || ctx.callbackQuery?.data || '';
    
    // Check if this is an exempt command
    const isExemptCommand = exemptCommands.some(cmd => 
      messageText.startsWith(cmd) || messageText.includes(cmd)
    );
    
    if (isExemptCommand) {
      log.debug(`Skipping rate limit for exempt command: ${messageText}`);
      return next();
    }

    // Skip rate limiting for callback queries that don't count as user actions
    if (ctx.callbackQuery && !ctx.callbackQuery.data?.startsWith('action_')) {
      return next();
    }

    const userId = ctx.from?.id;
    if (!userId) {
      log.warn('No user ID found in context, skipping rate limit');
      return next();
    }

    try {
      // Check and process the rate limit
      const rateLimitResult = await rateLimitService.processRequest(userId);
      
      if (!rateLimitResult.allowed) {
        // User has exceeded rate limit
        log.info(`User ${userId} exceeded rate limit: ${rateLimitResult.current}/${rateLimitResult.limit}`);
        
        // Calculate time until reset
        const resetMinutes = Math.ceil(rateLimitResult.resetIn / 60000);
        const resetSeconds = Math.ceil((rateLimitResult.resetIn % 60000) / 1000);
        
        // Send rate limit message
        const rateLimitMessage = ctx.t ? 
          ctx.t('rate_limit.exceeded', { 
            limit: rateLimitResult.limit,
            resetMinutes,
            resetSeconds,
            current: rateLimitResult.current
          }) :
          `⚠️ Превышен лимит запросов!\n\n` +
          `Вы превысили лимит в ${rateLimitResult.limit} запросов в минуту.\n` +
          `Текущий счетчик: ${rateLimitResult.current}/${rateLimitResult.limit}\n` +
          `Попробуйте снова через ${resetMinutes > 0 ? `${resetMinutes} мин` : `${resetSeconds} сек`}.\n\n` +
          `💡 Купите больше энергии для увеличения лимита запросов!`;

        // Try to reply to the message or send to chat
        if (ctx.message) {
          await ctx.reply(rateLimitMessage, { 
            reply_to_message_id: ctx.message.message_id,
            parse_mode: undefined // Don't use markdown to avoid parsing errors
          });
        } else if (ctx.callbackQuery) {
          await ctx.answerCallbackQuery(rateLimitMessage.slice(0, 200)); // Callback query answers are limited
          await ctx.editMessageText(rateLimitMessage);
        } else {
          await ctx.api.sendMessage(ctx.chat.id, rateLimitMessage);
        }
        
        // Don't continue processing the message
        return;
      }

      // Log successful rate limit check
      log.debug(`Rate limit OK for user ${userId}: ${rateLimitResult.current}/${rateLimitResult.limit}`);
      
      // Add rate limit info to context for debugging
      ctx.rateLimitInfo = rateLimitResult;
      
      // Continue processing the message
      return next();
      
    } catch (error) {
      log.error('Error in rate limit middleware:', () => error);
      
      // On error, allow the request to proceed to avoid blocking the bot
      return next();
    }
  };
}

/**
 * Admin middleware to check rate limit status
 * Can be used in admin commands to view user rate limits
 */
export function rateLimitStatusMiddleware() {
  return async (ctx, next) => {
    const userId = ctx.from?.id;
    if (userId && config.rateLimitEnabled) {
      try {
        const status = await rateLimitService.getStatus(userId);
        ctx.rateLimitStatus = status;
      } catch (error) {
        log.error('Error getting rate limit status:', () => error);
      }
    }
    return next();
  };
}