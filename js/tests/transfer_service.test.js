import { transferService } from '../src/services/transfer_service.js';

// Mock the dependencies
const mockTokenizeService = {
  get_tokens: jest.fn(),
  update_user_token: jest.fn()
};

const mockAsyncPost = jest.fn();

// Mock modules
jest.mock('../src/services/tokenize_service.js', () => ({
  tokenizeService: mockTokenizeService
}));

jest.mock('../src/services/utils.js', () => ({
  asyncPost: mockAsyncPost
}));

jest.mock('../src/bot/utils.js', () => ({
  getUserName: (id) => id.toString()
}));

jest.mock('../src/config.js', () => ({
  config: {
    adminToken: 'test-token',
    proxyUrl: 'http://test-proxy'
  }
}));

jest.mock('../src/utils/logger.js', () => ({
  createLogger: () => ({
    debug: jest.fn(),
    info: jest.fn(),
    error: jest.fn()
  })
}));

describe('TransferService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('validateTransfer', () => {
    test('should reject transfer to self', () => {
      const result = transferService.validateTransfer('123', '123', 1000);
      expect(result.valid).toBe(false);
      expect(result.code).toBe('CANNOT_TRANSFER_TO_SELF');
    });

    test('should reject invalid amounts', () => {
      expect(transferService.validateTransfer('123', '456', 0).valid).toBe(false);
      expect(transferService.validateTransfer('123', '456', -100).valid).toBe(false);
      expect(transferService.validateTransfer('123', '456', 1.5).valid).toBe(false);
    });

    test('should reject amounts below minimum', () => {
      const result = transferService.validateTransfer('123', '456', 50);
      expect(result.valid).toBe(false);
      expect(result.code).toBe('AMOUNT_TOO_SMALL');
      expect(result.minimum).toBe(transferService.MIN_TRANSFER_AMOUNT);
    });

    test('should reject amounts above maximum', () => {
      const result = transferService.validateTransfer('123', '456', 200000);
      expect(result.valid).toBe(false);
      expect(result.code).toBe('AMOUNT_TOO_LARGE');
      expect(result.maximum).toBe(transferService.MAX_TRANSFER_AMOUNT);
    });

    test('should accept valid transfers', () => {
      const result = transferService.validateTransfer('123', '456', 1000);
      expect(result.valid).toBe(true);
    });
  });

  describe('parseAmount', () => {
    test('should parse valid numbers', () => {
      expect(transferService.parseAmount('1000')).toBe(1000);
      expect(transferService.parseAmount('5000')).toBe(5000);
      expect(transferService.parseAmount(' 2500 ')).toBe(2500);
    });

    test('should remove non-digit characters', () => {
      expect(transferService.parseAmount('1,000')).toBe(1000);
      expect(transferService.parseAmount('5 000')).toBe(5000);
      expect(transferService.parseAmount('$2500')).toBe(2500);
    });

    test('should return null for invalid input', () => {
      expect(transferService.parseAmount('')).toBe(null);
      expect(transferService.parseAmount('abc')).toBe(null);
      expect(transferService.parseAmount(null)).toBe(null);
      expect(transferService.parseAmount(undefined)).toBe(null);
    });
  });

  describe('parseRecipient', () => {
    test('should parse valid user IDs', () => {
      expect(transferService.parseRecipient('123456789')).toBe('123456789');
      expect(transferService.parseRecipient(' 987654321 ')).toBe('987654321');
    });

    test('should return null for usernames (not supported)', () => {
      expect(transferService.parseRecipient('@username')).toBe(null);
      expect(transferService.parseRecipient('username')).toBe(null);
    });

    test('should return null for invalid input', () => {
      expect(transferService.parseRecipient('')).toBe(null);
      expect(transferService.parseRecipient('abc123')).toBe(null);
      expect(transferService.parseRecipient(null)).toBe(null);
    });
  });

  describe('transferEnergy', () => {
    test('should reject invalid transfer parameters', async () => {
      const result = await transferService.transferEnergy('123', '123', 1000);
      expect(result.success).toBe(false);
      expect(result.code).toBe('CANNOT_TRANSFER_TO_SELF');
    });

    test('should reject transfer when sender not found', async () => {
      mockTokenizeService.get_tokens.mockResolvedValue(null);
      
      const result = await transferService.transferEnergy('123', '456', 1000);
      expect(result.success).toBe(false);
      expect(result.code).toBe('SENDER_NOT_FOUND');
    });

    test('should reject transfer when insufficient balance', async () => {
      mockTokenizeService.get_tokens
        .mockResolvedValueOnce({ tokens: 500 }) // sender balance
        .mockResolvedValueOnce({ tokens: 1000 }); // recipient balance
      
      const result = await transferService.transferEnergy('123', '456', 1000);
      expect(result.success).toBe(false);
      expect(result.code).toBe('INSUFFICIENT_BALANCE');
    });

    test('should reject transfer when would leave insufficient remaining balance', async () => {
      mockTokenizeService.get_tokens
        .mockResolvedValueOnce({ tokens: 1500 }) // sender balance
        .mockResolvedValueOnce({ tokens: 1000 }); // recipient balance
      
      const result = await transferService.transferEnergy('123', '456', 1000);
      expect(result.success).toBe(false);
      expect(result.code).toBe('INSUFFICIENT_REMAINING_BALANCE');
    });

    test('should successfully transfer energy', async () => {
      mockTokenizeService.get_tokens
        .mockResolvedValueOnce({ tokens: 5000 }) // sender balance
        .mockResolvedValueOnce({ tokens: 2000 }); // recipient balance
      
      mockTokenizeService.update_user_token
        .mockResolvedValueOnce({ success: true }) // subtract from sender
        .mockResolvedValueOnce({ success: true }); // add to recipient
      
      mockAsyncPost.mockResolvedValue({ status: 200 });
      
      const result = await transferService.transferEnergy('123', '456', 1000);
      expect(result.success).toBe(true);
      expect(result.amount).toBe(1000);
      expect(result.senderNewBalance).toBe(4000);
      expect(result.recipientNewBalance).toBe(3000);
      
      expect(mockTokenizeService.update_user_token).toHaveBeenCalledWith('123', 1000, 'subtract');
      expect(mockTokenizeService.update_user_token).toHaveBeenCalledWith('456', 1000, 'add');
    });

    test('should rollback on failed recipient credit', async () => {
      mockTokenizeService.get_tokens
        .mockResolvedValueOnce({ tokens: 5000 }) // sender balance
        .mockResolvedValueOnce({ tokens: 2000 }); // recipient balance
      
      mockTokenizeService.update_user_token
        .mockResolvedValueOnce({ success: true }) // subtract from sender
        .mockResolvedValueOnce(null); // fail to add to recipient
      
      const result = await transferService.transferEnergy('123', '456', 1000);
      expect(result.success).toBe(false);
      expect(result.code).toBe('TRANSFER_FAILED');
      
      // Should have attempted rollback
      expect(mockTokenizeService.update_user_token).toHaveBeenCalledTimes(3);
      expect(mockTokenizeService.update_user_token).toHaveBeenLastCalledWith('123', 1000, 'add');
    });
  });
});