import { Composer, InlineKeyboard } from 'grammy';
import { transferService } from '../../services/transfer_service.js';
import { tokenizeService } from '../../services/tokenize_service.js';
import { createLogger } from '../../utils/logger.js';
import { sendMessage } from '../main_keyboard.js';

const log = createLogger('transfer_router');

export const transferRouter = new Composer();

// Store ongoing transfer sessions
const transferSessions = new Map();

/**
 * Start transfer command - shows transfer instructions
 */
transferRouter.command('transfer', async (ctx) => {
  log.debug('Transfer command triggered by user:', ctx.from.id);
  
  try {
    const userBalance = await tokenizeService.get_tokens(ctx.from.id);
    const currentTokens = userBalance?.tokens || 0;
    
    const keyboard = new InlineKeyboard()
      .text(ctx.t('transfer.start_transfer'), 'transfer_start')
      .row()
      .text(ctx.t('transfer.transfer_help'), 'transfer_help');
    
    await ctx.reply(ctx.t('transfer.welcome', { 
      balance: currentTokens.toLocaleString(),
      minAmount: transferService.MIN_TRANSFER_AMOUNT.toLocaleString(),
      maxAmount: transferService.MAX_TRANSFER_AMOUNT.toLocaleString(),
      minRemaining: transferService.MIN_REMAINING_BALANCE.toLocaleString()
    }), {
      reply_markup: keyboard,
      parse_mode: 'MarkdownV2'
    });
  } catch (error) {
    log.error('Error in transfer command:', error);
    await sendMessage(ctx, ctx.t('transfer.error'));
  }
});

/**
 * Handle transfer button from main keyboard
 */
transferRouter.hears(['🔄 Transfer', '🔄 Перевод'], async (ctx) => {
  // Same as /transfer command
  return transferRouter.command('transfer').call(this, ctx);
});

/**
 * Quick transfer command with parameters: /transfer <user_id> <amount>
 */
transferRouter.command('send', async (ctx) => {
  log.debug('Send command triggered by user:', ctx.from.id);
  
  const args = ctx.message.text.split(' ').slice(1); // Remove command
  
  if (args.length < 2) {
    await ctx.reply(ctx.t('transfer.send_usage'));
    return;
  }
  
  const recipientId = args[0];
  const amount = transferService.parseAmount(args[1]);
  
  if (!amount) {
    await ctx.reply(ctx.t('transfer.invalid_amount'));
    return;
  }
  
  if (!recipientId || recipientId === ctx.from.id.toString()) {
    await ctx.reply(ctx.t('transfer.invalid_recipient'));
    return;
  }
  
  await executeTransfer(ctx, ctx.from.id, recipientId, amount);
});

/**
 * Handle callback queries for transfer flow
 */
transferRouter.on('callback_query', async (ctx) => {
  const data = ctx.callbackQuery.data;
  const userId = ctx.from.id;
  
  if (data === 'transfer_start') {
    // Start interactive transfer flow
    await startTransferFlow(ctx, userId);
    return;
  }
  
  if (data === 'transfer_help') {
    await showTransferHelp(ctx);
    return;
  }
  
  if (data.startsWith('transfer_confirm_')) {
    const parts = data.split('_');
    const recipientId = parts[2];
    const amount = parseInt(parts[3]);
    
    await executeTransfer(ctx, userId, recipientId, amount);
    return;
  }
  
  if (data === 'transfer_cancel') {
    transferSessions.delete(userId);
    await ctx.editMessageText(ctx.t('transfer.cancelled'));
    return;
  }
});

/**
 * Handle text messages during transfer flow
 */
transferRouter.on('message:text', async (ctx) => {
  const userId = ctx.from.id;
  const session = transferSessions.get(userId);
  
  if (!session) return; // Not in transfer flow
  
  const text = ctx.message.text.trim();
  
  if (session.step === 'waiting_recipient') {
    // Parse recipient
    const recipientId = transferService.parseRecipient(text);
    
    if (!recipientId) {
      await ctx.reply(ctx.t('transfer.invalid_recipient_format'));
      return;
    }
    
    if (recipientId === userId.toString()) {
      await ctx.reply(ctx.t('transfer.cannot_transfer_to_self'));
      return;
    }
    
    // Check if recipient exists
    try {
      const recipientBalance = await tokenizeService.get_tokens(recipientId);
      if (!recipientBalance) {
        await ctx.reply(ctx.t('transfer.recipient_not_found'));
        return;
      }
      
      session.recipientId = recipientId;
      session.step = 'waiting_amount';
      
      await ctx.reply(ctx.t('transfer.enter_amount', {
        minAmount: transferService.MIN_TRANSFER_AMOUNT.toLocaleString(),
        maxAmount: transferService.MAX_TRANSFER_AMOUNT.toLocaleString()
      }));
      
    } catch (error) {
      log.error('Error checking recipient:', error);
      await ctx.reply(ctx.t('transfer.recipient_not_found'));
    }
    
    return;
  }
  
  if (session.step === 'waiting_amount') {
    // Parse amount
    const amount = transferService.parseAmount(text);
    
    if (!amount) {
      await ctx.reply(ctx.t('transfer.invalid_amount_format'));
      return;
    }
    
    // Validate amount
    const validation = transferService.validateTransfer(userId.toString(), session.recipientId, amount);
    if (!validation.valid) {
      await ctx.reply(getErrorMessage(ctx, validation.error, validation));
      return;
    }
    
    // Check balance
    try {
      const userBalance = await tokenizeService.get_tokens(userId);
      const currentTokens = userBalance?.tokens || 0;
      
      if (currentTokens < amount) {
        await ctx.reply(ctx.t('transfer.insufficient_balance', {
          current: currentTokens.toLocaleString(),
          required: amount.toLocaleString()
        }));
        return;
      }
      
      if ((currentTokens - amount) < transferService.MIN_REMAINING_BALANCE) {
        await ctx.reply(ctx.t('transfer.insufficient_remaining_balance', {
          current: currentTokens.toLocaleString(),
          required: amount.toLocaleString(),
          minRemaining: transferService.MIN_REMAINING_BALANCE.toLocaleString()
        }));
        return;
      }
      
      // Show confirmation
      await showTransferConfirmation(ctx, session.recipientId, amount);
      transferSessions.delete(userId); // Clear session
      
    } catch (error) {
      log.error('Error validating transfer:', error);
      await ctx.reply(ctx.t('transfer.error'));
      transferSessions.delete(userId);
    }
    
    return;
  }
});

/**
 * Start interactive transfer flow
 */
async function startTransferFlow(ctx, userId) {
  transferSessions.set(userId, {
    step: 'waiting_recipient',
    recipientId: null,
    amount: null
  });
  
  await ctx.editMessageText(ctx.t('transfer.enter_recipient'));
}

/**
 * Show transfer help
 */
async function showTransferHelp(ctx) {
  await ctx.editMessageText(ctx.t('transfer.help'), {
    parse_mode: 'MarkdownV2',
    reply_markup: new InlineKeyboard()
      .text(ctx.t('transfer.back'), 'transfer_start')
  });
}

/**
 * Show transfer confirmation
 */
async function showTransferConfirmation(ctx, recipientId, amount) {
  const keyboard = new InlineKeyboard()
    .text(ctx.t('transfer.confirm'), `transfer_confirm_${recipientId}_${amount}`)
    .text(ctx.t('transfer.cancel'), 'transfer_cancel')
    .row();
  
  await ctx.reply(ctx.t('transfer.confirmation', {
    recipient: recipientId,
    amount: amount.toLocaleString()
  }), {
    reply_markup: keyboard
  });
}

/**
 * Execute the actual transfer
 */
async function executeTransfer(ctx, fromUserId, toUserId, amount) {
  try {
    log.debug('Executing transfer:', { fromUserId, toUserId, amount });
    
    const result = await transferService.transferEnergy(
      fromUserId.toString(), 
      toUserId.toString(), 
      amount
    );
    
    if (result.success) {
      await ctx.reply(ctx.t('transfer.success', {
        amount: amount.toLocaleString(),
        recipient: toUserId,
        newBalance: result.senderNewBalance.toLocaleString()
      }));
      
      // Try to notify recipient
      try {
        await ctx.api.sendMessage(toUserId, ctx.t('transfer.received', {
          amount: amount.toLocaleString(),
          sender: fromUserId,
          newBalance: result.recipientNewBalance.toLocaleString()
        }));
      } catch (error) {
        log.debug('Could not notify recipient:', error.message);
        // Don't fail the transfer if we can't notify
      }
      
    } else {
      await ctx.reply(getErrorMessage(ctx, result.code, result));
    }
    
  } catch (error) {
    log.error('Transfer execution error:', error);
    await ctx.reply(ctx.t('transfer.error'));
  }
  
  // Clean up session
  transferSessions.delete(fromUserId);
}

/**
 * Get localized error message
 */
function getErrorMessage(ctx, errorCode, errorData = {}) {
  switch (errorCode) {
    case 'CANNOT_TRANSFER_TO_SELF':
      return ctx.t('transfer.cannot_transfer_to_self');
    case 'INVALID_AMOUNT':
      return ctx.t('transfer.invalid_amount');
    case 'AMOUNT_TOO_SMALL':
      return ctx.t('transfer.amount_too_small', { minimum: errorData.minimum?.toLocaleString() });
    case 'AMOUNT_TOO_LARGE':
      return ctx.t('transfer.amount_too_large', { maximum: errorData.maximum?.toLocaleString() });
    case 'INSUFFICIENT_BALANCE':
      return ctx.t('transfer.insufficient_balance', {
        current: errorData.current?.toLocaleString(),
        required: errorData.required?.toLocaleString()
      });
    case 'INSUFFICIENT_REMAINING_BALANCE':
      return ctx.t('transfer.insufficient_remaining_balance', {
        current: errorData.current?.toLocaleString(),
        required: errorData.required?.toLocaleString(),
        minRemaining: errorData.minRemaining?.toLocaleString()
      });
    case 'RECIPIENT_NOT_FOUND':
      return ctx.t('transfer.recipient_not_found');
    case 'SENDER_NOT_FOUND':
      return ctx.t('transfer.sender_not_found');
    case 'TRANSFER_FAILED':
      return ctx.t('transfer.failed');
    default:
      return ctx.t('transfer.error');
  }
}