import { apiPriorityService } from '../src/services/api_priority_service.js';

// Test the API priority service
async function testApiPriorityService() {
  console.log('Testing API Priority Service...\n');

  // Test 1: Get best API for different models
  console.log('=== Test 1: Model-specific API selection ===');
  
  const testModels = [
    'claude-3-5-sonnet',
    'gpt-4o',
    'meta-llama/Meta-Llama-3.1-70B',
    'deepseek-chat',
    'o1-mini'
  ];

  for (const model of testModels) {
    const bestApi = apiPriorityService.getBestApiForModel(model);
    console.log(`Model: ${model.padEnd(30)} -> Provider: ${bestApi.id} (${bestApi.url})`);
  }

  console.log('\n=== Test 2: Provider status ===');
  const status = apiPriorityService.getProviderStatus();
  status.forEach(provider => {
    console.log(`Provider: ${provider.id.padEnd(12)} | Health: ${provider.healthScore}% | Healthy: ${provider.isHealthy} | Rate Limited: ${provider.isRateLimited}`);
  });

  console.log('\n=== Test 3: Context-aware selection ===');
  const textContext = { hasMedia: false };
  const mediaContext = { hasMedia: true };

  const gpt4oText = apiPriorityService.getBestApiForModel('gpt-4o', textContext);
  const gpt4oMedia = apiPriorityService.getBestApiForModel('gpt-4o', mediaContext);

  console.log(`GPT-4o (text):  ${gpt4oText.id}`);
  console.log(`GPT-4o (media): ${gpt4oMedia.id}`);

  console.log('\n=== Test 4: Recording successes and failures ===');
  
  // Simulate some API calls
  apiPriorityService.recordSuccess('primary', 500, 100);
  apiPriorityService.recordSuccess('deepinfra', 800, 150);
  apiPriorityService.recordFailure('goapi', new Error('Connection timeout'));
  
  console.log('After recording some API results:');
  const statusAfter = apiPriorityService.getProviderStatus();
  statusAfter.forEach(provider => {
    console.log(`Provider: ${provider.id.padEnd(12)} | Health: ${provider.healthScore}% | Avg Response: ${provider.avgResponseTime}ms | Failures: ${provider.recentFailures}`);
  });

  console.log('\n=== Test 5: Adding/removing providers ===');
  
  // Add a new provider
  apiPriorityService.addProvider('test-provider', {
    url: 'https://test.api.com',
    priority: 4,
    capabilities: {
      claude: false,
      gpt: true,
      llama: false,
      deepseek: false,
      o1: false,
      multimodal: false,
      streaming: true
    },
    rateLimits: {
      requestsPerMinute: 10,
      tokensPerMinute: 10000
    }
  });

  console.log('Added test provider');
  const statusWithNew = apiPriorityService.getProviderStatus();
  console.log(`Total providers: ${statusWithNew.length}`);

  // Remove the test provider
  apiPriorityService.removeProvider('test-provider');
  console.log('Removed test provider');

  console.log('\n=== Test completed successfully! ===');
}

// Run the test
if (import.meta.main) {
  testApiPriorityService().catch(console.error);
}

export { testApiPriorityService };