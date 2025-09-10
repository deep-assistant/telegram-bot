import { completionsService } from '../src/services/index.js';

// Test the message length validation and history cutting functionality
async function testMessageLengthValidation() {
  console.log('🧪 Testing message length validation...');
  
  // Test 1: String message validation
  console.log('📝 Test 1: String message validation');
  const longMessage = 'a'.repeat(5000); // 5000 characters
  const validatedMessage = completionsService.validateMessageLength(longMessage, 4000);
  
  if (validatedMessage.length <= 4000) {
    console.log('✅ Long string message correctly truncated');
    console.log(`   Original length: ${longMessage.length}, Validated length: ${validatedMessage.length}`);
  } else {
    console.log('❌ String message not properly truncated');
  }
  
  // Test 2: Array content validation (multimodal)
  console.log('📝 Test 2: Array content validation');
  const longTextContent = [
    { type: 'text', text: 'Short text' },
    { type: 'text', text: 'b'.repeat(4000) }, // Very long text
    { type: 'image_url', image_url: { url: 'https://example.com/image.jpg' } }
  ];
  
  const validatedArray = completionsService.validateMessageLength(longTextContent, 4000);
  let totalTextLength = 0;
  for (const item of validatedArray) {
    if (item.type === 'text' && item.text) {
      totalTextLength += item.text.length;
    }
  }
  
  if (totalTextLength <= 4000) {
    console.log('✅ Array content correctly truncated');
    console.log(`   Total text length after validation: ${totalTextLength}`);
  } else {
    console.log('❌ Array content not properly truncated');
  }
  
  // Test 3: History cutting
  console.log('📝 Test 3: History cutting functionality');
  const testUserId = 'test_user_123';
  
  // Clear any existing history
  completionsService.clearHistory(testUserId);
  
  // Add several long messages to history
  for (let i = 0; i < 10; i++) {
    completionsService.updateHistory(testUserId, {
      role: 'user',
      content: `Message ${i}: ${'x'.repeat(500)}`
    });
    completionsService.updateHistory(testUserId, {
      role: 'assistant', 
      content: `Response ${i}: ${'y'.repeat(500)}`
    });
  }
  
  const historyBefore = completionsService.getHistory(testUserId);
  console.log(`   History before cutting: ${historyBefore.length} items`);
  
  // Cut history
  completionsService.cutHistory(testUserId);
  
  const historyAfter = completionsService.getHistory(testUserId);
  console.log(`   History after cutting: ${historyAfter.length} items`);
  
  // Calculate total length
  let totalLength = 0;
  for (const item of historyAfter) {
    if (typeof item === 'string') {
      totalLength += item.length;
    } else if (item && item.content) {
      totalLength += String(item.content).length;
    } else {
      totalLength += JSON.stringify(item).length;
    }
  }
  
  if (totalLength <= 4000 && historyAfter.length < historyBefore.length) {
    console.log('✅ History correctly cut to prevent length issues');
    console.log(`   Total length after cutting: ${totalLength} characters`);
  } else {
    console.log('❌ History cutting not working properly');
    console.log(`   Total length: ${totalLength}, Items: ${historyAfter.length}`);
  }
  
  // Test 4: Edge cases
  console.log('📝 Test 4: Edge cases');
  
  // Test null/undefined
  const nullResult = completionsService.validateMessageLength(null);
  const undefinedResult = completionsService.validateMessageLength(undefined);
  
  if (nullResult === null && undefinedResult === undefined) {
    console.log('✅ Null/undefined values handled correctly');
  } else {
    console.log('❌ Null/undefined values not handled correctly');
  }
  
  // Test empty string
  const emptyResult = completionsService.validateMessageLength('');
  if (emptyResult === '') {
    console.log('✅ Empty string handled correctly');
  } else {
    console.log('❌ Empty string not handled correctly');
  }
  
  // Test short message (should remain unchanged)
  const shortMessage = 'This is a short message';
  const shortResult = completionsService.validateMessageLength(shortMessage);
  if (shortResult === shortMessage) {
    console.log('✅ Short messages remain unchanged');
  } else {
    console.log('❌ Short messages incorrectly modified');
  }
  
  console.log('🎉 Message length validation tests completed');
}

// Test the method name fix
async function testMethodNames() {
  console.log('🧪 Testing method name consistency...');
  
  // Check if query_chatgpt method exists
  if (typeof completionsService.query_chatgpt === 'function') {
    console.log('✅ query_chatgpt method exists');
  } else {
    console.log('❌ query_chatgpt method missing');
  }
  
  // Check if queryChatGPT method still exists
  if (typeof completionsService.queryChatGPT === 'function') {
    console.log('✅ queryChatGPT method exists');
  } else {
    console.log('❌ queryChatGPT method missing');
  }
  
  console.log('🎉 Method name tests completed');
}

// Run tests
async function runTests() {
  console.log('🚀 Starting message length and method consistency tests...');
  
  try {
    await testMessageLengthValidation();
    await testMethodNames();
    console.log('✅ All tests completed successfully');
  } catch (error) {
    console.error('❌ Tests failed:', error);
    throw error;
  }
}

// Execute tests if this file is run directly
if (import.meta.main) {
  await runTests();
}

export { runTests };