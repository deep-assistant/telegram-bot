// Simple validation script for API priority service
import { apiPriorityService } from './src/services/api_priority_service.js';

console.log('Testing API Priority Service...');

try {
  // Test basic functionality
  const claudeApi = apiPriorityService.getBestApiForModel('claude-3-5-sonnet');
  console.log(`✓ Claude model gets API: ${claudeApi.id}`);

  const gptApi = apiPriorityService.getBestApiForModel('gpt-4o');
  console.log(`✓ GPT model gets API: ${gptApi.id}`);

  const llamaApi = apiPriorityService.getBestApiForModel('meta-llama/Meta-Llama-3.1-70B');
  console.log(`✓ Llama model gets API: ${llamaApi.id}`);

  // Test provider status
  const status = apiPriorityService.getProviderStatus();
  console.log(`✓ Provider status retrieved: ${status.length} providers`);

  // Test recording
  apiPriorityService.recordSuccess('primary', 500, 100);
  console.log('✓ Success recording works');

  apiPriorityService.recordFailure('goapi', new Error('Test error'));
  console.log('✓ Failure recording works');

  console.log('\n✅ All basic API priority tests passed!');
  
  // Clean up
  apiPriorityService.destroy();
  
} catch (error) {
  console.error('❌ Test failed:', error.message);
  process.exit(1);
}