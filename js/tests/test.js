import { tokenizeService, GPTModels } from '../src/services/index.js';

async function hello() {
  console.log('Testing tokenize service...');
  try {
    // Test getting tokens (should create new if not exists)
    const tokens = await tokenizeService.get_tokens(1495307231);
    console.log('get_tokens result:', tokens);
    
    // Test getting user tokens directly
    const userTokens = await tokenizeService.getUserTokens(1495307231);
    console.log('getUserTokens result:', userTokens);
    
    // Test updating user tokens
    const updateResult = await tokenizeService.update_user_token(1495307231, 10000);
    console.log('update_user_token result:', updateResult);
    
    // Test getting tokens again after update
    const tokensAfterUpdate = await tokenizeService.get_tokens(1495307231);
    console.log('get_tokens after update:', tokensAfterUpdate);
    
  } catch (error) {
    console.error('Test failed with error:', error);
  }
}

hello().catch(console.error);

