import { config } from '../config.js';
import { tokenizeService } from './tokenize_service.js';
import { asyncPost } from './utils.js';
import { getUserName } from '../bot/utils.js';
import { createLogger } from '../utils/logger.js';

const log = createLogger('transfer_service');

class TransferService {
  constructor() {
    this.MIN_TRANSFER_AMOUNT = 100; // Minimum 100⚡️ to transfer
    this.MAX_TRANSFER_AMOUNT = 100000; // Maximum 100,000⚡️ per transfer
    this.MIN_REMAINING_BALANCE = 1000; // User must keep at least 1,000⚡️
  }

  /**
   * Transfer energy between users
   * @param {string} fromUserId - Sender's Telegram ID
   * @param {string} toUserId - Recipient's Telegram ID  
   * @param {number} amount - Amount of energy to transfer
   * @returns {Object} Transfer result with success status and message
   */
  async transferEnergy(fromUserId, toUserId, amount) {
    try {
      log.debug('Transfer request:', { fromUserId, toUserId, amount });

      // Validate input parameters
      const validation = this.validateTransfer(fromUserId, toUserId, amount);
      if (!validation.valid) {
        return { success: false, error: validation.error, code: validation.code };
      }

      // Check sender's balance
      const senderBalance = await tokenizeService.get_tokens(fromUserId);
      if (!senderBalance) {
        return { success: false, error: 'SENDER_NOT_FOUND', code: 'SENDER_NOT_FOUND' };
      }

      // Validate sender has enough balance
      const currentTokens = senderBalance.tokens || 0;
      if (currentTokens < amount) {
        return { 
          success: false, 
          error: 'INSUFFICIENT_BALANCE',
          code: 'INSUFFICIENT_BALANCE',
          current: currentTokens,
          required: amount
        };
      }

      // Validate sender will have minimum remaining balance
      if ((currentTokens - amount) < this.MIN_REMAINING_BALANCE) {
        return { 
          success: false, 
          error: 'INSUFFICIENT_REMAINING_BALANCE',
          code: 'INSUFFICIENT_REMAINING_BALANCE',
          current: currentTokens,
          required: amount,
          minRemaining: this.MIN_REMAINING_BALANCE
        };
      }

      // Check if recipient exists (try to get their tokens, create if doesn't exist)
      const recipientBalance = await tokenizeService.get_tokens(toUserId);
      if (!recipientBalance) {
        return { success: false, error: 'RECIPIENT_NOT_FOUND', code: 'RECIPIENT_NOT_FOUND' };
      }

      // Perform the transfer (subtract from sender, add to recipient)
      const subtractResult = await tokenizeService.update_user_token(fromUserId, amount, 'subtract');
      if (!subtractResult) {
        return { success: false, error: 'TRANSFER_FAILED_SUBTRACT', code: 'TRANSFER_FAILED' };
      }

      const addResult = await tokenizeService.update_user_token(toUserId, amount, 'add');
      if (!addResult) {
        // Rollback: add back to sender
        await tokenizeService.update_user_token(fromUserId, amount, 'add');
        return { success: false, error: 'TRANSFER_FAILED_ADD', code: 'TRANSFER_FAILED' };
      }

      // Log the successful transfer
      await this.logTransfer(fromUserId, toUserId, amount);

      log.info('Transfer completed successfully:', { fromUserId, toUserId, amount });

      return { 
        success: true, 
        amount,
        senderNewBalance: (currentTokens - amount),
        recipientNewBalance: (recipientBalance.tokens || 0) + amount
      };

    } catch (error) {
      log.error('Transfer error:', error);
      return { success: false, error: 'TRANSFER_ERROR', code: 'TRANSFER_ERROR', details: error.message };
    }
  }

  /**
   * Validate transfer parameters
   * @param {string} fromUserId 
   * @param {string} toUserId 
   * @param {number} amount 
   * @returns {Object} Validation result
   */
  validateTransfer(fromUserId, toUserId, amount) {
    // Check if trying to transfer to self
    if (fromUserId === toUserId) {
      return { valid: false, error: 'CANNOT_TRANSFER_TO_SELF', code: 'CANNOT_TRANSFER_TO_SELF' };
    }

    // Validate amount is a positive number
    if (!amount || amount <= 0 || !Number.isInteger(amount)) {
      return { valid: false, error: 'INVALID_AMOUNT', code: 'INVALID_AMOUNT' };
    }

    // Check minimum transfer amount
    if (amount < this.MIN_TRANSFER_AMOUNT) {
      return { 
        valid: false, 
        error: 'AMOUNT_TOO_SMALL', 
        code: 'AMOUNT_TOO_SMALL',
        minimum: this.MIN_TRANSFER_AMOUNT 
      };
    }

    // Check maximum transfer amount
    if (amount > this.MAX_TRANSFER_AMOUNT) {
      return { 
        valid: false, 
        error: 'AMOUNT_TOO_LARGE', 
        code: 'AMOUNT_TOO_LARGE',
        maximum: this.MAX_TRANSFER_AMOUNT 
      };
    }

    return { valid: true };
  }

  /**
   * Log transfer for audit purposes
   * @param {string} fromUserId 
   * @param {string} toUserId 
   * @param {number} amount 
   */
  async logTransfer(fromUserId, toUserId, amount) {
    try {
      const transferLog = {
        from: getUserName(fromUserId),
        to: getUserName(toUserId),
        amount,
        timestamp: new Date().toISOString(),
        type: 'energy_transfer'
      };

      // Log to proxy service if endpoint exists
      const params = { masterToken: config.adminToken };
      const payload = transferLog;
      
      try {
        await asyncPost(`${config.proxyUrl}/transfer-log`, { params, json: payload });
      } catch (error) {
        // Log locally if remote logging fails
        log.info('Transfer completed (remote log failed):', transferLog);
      }
    } catch (error) {
      log.error('Failed to log transfer:', error);
    }
  }

  /**
   * Parse recipient from text input (username, user ID, or mention)
   * @param {string} recipientText - Text input from user
   * @returns {string|null} User ID if found, null otherwise  
   */
  parseRecipient(recipientText) {
    if (!recipientText) return null;

    const text = recipientText.trim();
    
    // If it's a pure number (user ID)
    if (/^\d+$/.test(text)) {
      return text;
    }

    // If it's a mention format (@username or t.me/username)
    const mentionMatch = text.match(/@(\w+)/);
    if (mentionMatch) {
      // Note: This would require a username-to-ID lookup service
      // For now, we'll return null and suggest using user ID
      return null;
    }

    return null;
  }

  /**
   * Parse amount from text input
   * @param {string} amountText - Text input from user
   * @returns {number|null} Parsed amount or null if invalid
   */
  parseAmount(amountText) {
    if (!amountText) return null;

    const text = amountText.trim().replace(/[^\d]/g, ''); // Remove non-digits
    const amount = parseInt(text, 10);
    
    if (isNaN(amount) || amount <= 0) return null;
    
    return amount;
  }
}

export const transferService = new TransferService();