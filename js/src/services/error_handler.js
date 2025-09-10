/**
 * Error handling utilities for image generation services.
 */

/**
 * Parse Midjourney API error response and return user-friendly message.
 * 
 * @param {Object} errorData - The error object from Midjourney API response
 * @returns {string|null} User-friendly error message or null if no specific handling
 */
export function parseMidjourneyError(errorData) {
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

/**
 * Get user-friendly error message from service result data.
 * 
 * @param {Object} resultData - The result from image generation service
 * @param {string} serviceName - Name of the service for generic messages
 * @returns {string|null} User-friendly error message or null if no error
 */
export function getUserFriendlyErrorMessage(resultData, serviceName = "image generation") {
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