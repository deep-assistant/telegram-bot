import { rateLimitService } from '../src/services/rate_limit_service.js';
import { tokenizeService } from '../src/services/tokenize_service.js';
import { dataBase, dbKey } from '../src/db/init_db.js';

/**
 * Simple test for rate limiting functionality
 * This is a basic integration test to verify the rate limiting works
 */

// Mock user IDs for testing
const TEST_USER_ID = 12345;
const PREMIUM_USER_ID = 67890;

// Helper function to wait
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to clear test data
async function clearTestData(userId) {
  try {
    await dataBase.set(dbKey(userId, 'rate_limit'), '0');
    await dataBase.set(dbKey(userId, 'rate_limit_reset'), '0');
    await dataBase.commit();
  } catch (error) {
    console.log('Error clearing test data:', error.message);
  }
}

// Mock tokenizeService for testing
const originalGetTokens = tokenizeService.get_tokens;
tokenizeService.get_tokens = async (userId) => {
  console.log(`Mock: Getting tokens for user ${userId}`);
  if (userId === PREMIUM_USER_ID) {
    return { tokens: 60000 }; // Premium user with high energy
  }
  return { tokens: 1000 }; // Regular user with low energy
};

async function testBasicRateLimit() {
  console.log('🧪 Testing basic rate limit functionality...');
  
  await clearTestData(TEST_USER_ID);
  
  // First request should be allowed
  const result1 = await rateLimitService.processRequest(TEST_USER_ID);
  console.log('First request:', result1);
  
  if (!result1.allowed) {
    throw new Error('First request should be allowed');
  }
  
  // Multiple requests within limit should be allowed
  for (let i = 2; i <= 10; i++) {
    const result = await rateLimitService.processRequest(TEST_USER_ID);
    console.log(`Request ${i}:`, result);
    
    if (!result.allowed) {
      throw new Error(`Request ${i} should be allowed (limit not reached)`);
    }
  }
  
  // 11th request should be denied (default limit is 10)
  const result11 = await rateLimitService.processRequest(TEST_USER_ID);
  console.log('11th request (should be denied):', result11);
  
  if (result11.allowed) {
    throw new Error('11th request should be denied (exceeded limit)');
  }
  
  console.log('✅ Basic rate limit test passed');
}

async function testPremiumRateLimit() {
  console.log('🧪 Testing premium user rate limits...');
  
  await clearTestData(PREMIUM_USER_ID);
  
  // Premium user should have higher limits
  const status = await rateLimitService.getStatus(PREMIUM_USER_ID);
  console.log('Premium user status:', status);
  
  if (status.limit <= 10) {
    throw new Error('Premium user should have higher rate limit');
  }
  
  // Test premium user can make more requests
  for (let i = 1; i <= 15; i++) {
    const result = await rateLimitService.processRequest(PREMIUM_USER_ID);
    console.log(`Premium request ${i}:`, result);
    
    if (!result.allowed) {
      throw new Error(`Premium request ${i} should be allowed`);
    }
  }
  
  console.log('✅ Premium rate limit test passed');
}

async function testRateLimitReset() {
  console.log('🧪 Testing rate limit reset...');
  
  await clearTestData(TEST_USER_ID);
  
  // Fill up the rate limit
  for (let i = 1; i <= 10; i++) {
    await rateLimitService.processRequest(TEST_USER_ID);
  }
  
  // Next request should be denied
  const deniedResult = await rateLimitService.processRequest(TEST_USER_ID);
  if (deniedResult.allowed) {
    throw new Error('Request should be denied after reaching limit');
  }
  
  // Manually reset by simulating time passing (set reset time to past)
  const currentMinute = Math.floor(Date.now() / 60000);
  await dataBase.set(dbKey(TEST_USER_ID, 'rate_limit_reset'), (currentMinute - 1).toString());
  await dataBase.commit();
  
  // Next request should be allowed after reset
  const allowedResult = await rateLimitService.processRequest(TEST_USER_ID);
  console.log('Request after reset:', allowedResult);
  
  if (!allowedResult.allowed) {
    throw new Error('Request should be allowed after reset');
  }
  
  console.log('✅ Rate limit reset test passed');
}

async function testGetStatus() {
  console.log('🧪 Testing status functionality...');
  
  await clearTestData(TEST_USER_ID);
  
  const status = await rateLimitService.getStatus(TEST_USER_ID);
  console.log('User status:', status);
  
  if (typeof status.userId !== 'number') {
    throw new Error('Status should include user ID');
  }
  
  if (typeof status.limit !== 'number') {
    throw new Error('Status should include rate limit');
  }
  
  if (typeof status.current !== 'number') {
    throw new Error('Status should include current count');
  }
  
  console.log('✅ Status test passed');
}

// Run all tests
async function runTests() {
  console.log('🚀 Starting rate limit tests...\n');
  
  try {
    await testBasicRateLimit();
    console.log('');
    
    await testPremiumRateLimit();
    console.log('');
    
    await testRateLimitReset();
    console.log('');
    
    await testGetStatus();
    console.log('');
    
    console.log('🎉 All rate limit tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  } finally {
    // Restore original function
    tokenizeService.get_tokens = originalGetTokens;
    
    // Clean up test data
    await clearTestData(TEST_USER_ID);
    await clearTestData(PREMIUM_USER_ID);
  }
}

// Run tests if this file is executed directly
if (import.meta.main) {
  runTests().catch(console.error);
}

export { runTests };