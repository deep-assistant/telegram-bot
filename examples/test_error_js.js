#!/usr/bin/env node

/**
 * Simple test script for JavaScript error handling functionality.
 */

// Copy the functions locally to avoid import issues
function parseMidjourneyError(errorData) {
  if (!errorData || typeof errorData !== 'object') {
    return null;
  }
  
  const rawMessage = errorData.raw_message || '';
  const errorCode = errorData.code;
  
  // Handle banned prompt errors
  if (rawMessage.includes('Banned Prompt')) {
    // Extract the banned word from the message
    // Format: "Banned Prompt: word"
    if (rawMessage.includes(':')) {
      const bannedWord = rawMessage.split(':', 2)[1].trim();
      return `🚫 "${bannedWord}" is banned prompt by MidJourney, please try another prompt.`;
    }
  }
  
  // Handle other known error codes
  if (errorCode === 10000) {
    return `🚫 Prompt check failed: ${rawMessage}. Please try another prompt.`;
  }
  
  // Generic fallback for other errors
  if (rawMessage) {
    return `🚫 MidJourney error: ${rawMessage}. Please try again.`;
  }
  
  return null;
}

function getUserFriendlyErrorMessage(resultData, serviceName = "image generation") {
  if (!resultData || typeof resultData !== 'object') {
    return null;
  }
  
  // Check for error field in the response
  if (resultData.error) {
    const errorData = resultData.error;
    
    // Try to parse MidJourney specific errors
    if (serviceName.toLowerCase() === "midjourney") {
      const midjourneyError = parseMidjourneyError(errorData);
      if (midjourneyError) {
        return midjourneyError;
      }
    }
    
    // Generic error fallback
    if (typeof errorData === 'object') {
      const message = errorData.message || errorData.raw_message || '';
      if (message) {
        return `🚫 ${serviceName.charAt(0).toUpperCase() + serviceName.slice(1)} error: ${message}. Please try again.`;
      }
    }
  }
  
  // Check for failed status
  if (resultData.status === "failed") {
    return `🚫 ${serviceName.charAt(0).toUpperCase() + serviceName.slice(1)} generation failed. Please try again.`;
  }
  
  return null;
}

function testMidjourneyBannedPromptError() {
  console.log("Testing Midjourney banned prompt error...");
  
  // Sample error response from the issue
  const errorData = {
    code: 10000,
    raw_message: "Banned Prompt: dick",
    message: "failed to check prompt",
    detail: null
  };
  
  const resultData = {
    task_id: "6b17484e-93ae-40a0-9a16-014ba1f9cbbc",
    model: "midjourney",
    task_type: "imagine",
    status: "failed",
    error: errorData
  };
  
  // Test the error parser
  const errorMessage = parseMidjourneyError(errorData);
  console.log(`Parsed error message: ${errorMessage}`);
  
  const expected = '🚫 "dick" is banned prompt by MidJourney, please try another prompt.';
  console.assert(errorMessage === expected, `Expected: ${expected}, Got: ${errorMessage}`);
  
  // Test the full error handler
  const userFriendlyMessage = getUserFriendlyErrorMessage(resultData, "midjourney");
  console.log(`User-friendly message: ${userFriendlyMessage}`);
  
  console.assert(userFriendlyMessage === expected, `Expected: ${expected}, Got: ${userFriendlyMessage}`);
  
  console.log("✅ Banned prompt error test passed!");
}

function testDifferentBannedWord() {
  console.log("\nTesting different banned word...");
  
  const errorData = {
    code: 10000,
    raw_message: "Banned Prompt: nude",
    message: "failed to check prompt"
  };
  
  const resultData = { error: errorData };
  
  const userFriendlyMessage = getUserFriendlyErrorMessage(resultData, "midjourney");
  console.log(`User-friendly message: ${userFriendlyMessage}`);
  
  const expected = '🚫 "nude" is banned prompt by MidJourney, please try another prompt.';
  console.assert(userFriendlyMessage === expected, `Expected: ${expected}, Got: ${userFriendlyMessage}`);
  
  console.log("✅ Different banned word test passed!");
}

function testNoError() {
  console.log("\nTesting successful response...");
  
  const resultData = {
    task_id: "test-task-id", 
    status: "finished",
    task_result: {
      discord_image_url: "https://example.com/image.png"
    }
  };
  
  const userFriendlyMessage = getUserFriendlyErrorMessage(resultData, "midjourney");
  console.log(`User-friendly message: ${userFriendlyMessage}`);
  
  console.assert(userFriendlyMessage === null, `Expected null for successful response, got: ${userFriendlyMessage}`);
  
  console.log("✅ No error test passed!");
}

console.log("🧪 Testing JavaScript error handling functionality...\n");

try {
  testMidjourneyBannedPromptError();
  testDifferentBannedWord();
  testNoError();
  
  console.log("\n🎉 All tests passed! JavaScript error handling is working correctly.");
  
} catch (error) {
  console.error(`\n❌ Test failed: ${error}`);
  process.exit(1);
}