#!/usr/bin/env python3
"""
Simple test script for error handling functionality without service dependencies.
"""

def parse_midjourney_error(error_data):
    """
    Parse Midjourney API error response and return user-friendly message.
    """
    if not error_data or not isinstance(error_data, dict):
        return None
        
    raw_message = error_data.get('raw_message', '')
    error_code = error_data.get('code')
    
    # Handle banned prompt errors
    if 'Banned Prompt' in raw_message:
        # Extract the banned word from the message
        # Format: "Banned Prompt: word"
        if ':' in raw_message:
            banned_word = raw_message.split(':', 1)[1].strip()
            return f'🚫 "{banned_word}" is banned prompt by MidJourney, please try another prompt.'
    
    # Handle other known error codes
    if error_code == 10000:
        return f'🚫 Prompt check failed: {raw_message}. Please try another prompt.'
    
    # Generic fallback for other errors
    if raw_message:
        return f'🚫 MidJourney error: {raw_message}. Please try again.'
    
    return None


def get_user_friendly_error_message(result_data, service_name="image generation"):
    """
    Get user-friendly error message from service result data.
    """
    if not result_data or not isinstance(result_data, dict):
        return None
    
    # Check for error field in the response
    if "error" in result_data:
        error_data = result_data["error"]
        
        # Try to parse MidJourney specific errors
        if service_name.lower() == "midjourney":
            midjourney_error = parse_midjourney_error(error_data)
            if midjourney_error:
                return midjourney_error
        
        # Generic error fallback
        if isinstance(error_data, dict):
            message = error_data.get('message', error_data.get('raw_message', ''))
            if message:
                return f'🚫 {service_name.title()} error: {message}. Please try again.'
    
    # Check for failed status
    if result_data.get("status") == "failed":
        return f'🚫 {service_name.title()} generation failed. Please try again.'
    
    return None


def test_midjourney_banned_prompt_error():
    """Test handling of banned prompt errors."""
    print("Testing Midjourney banned prompt error...")
    
    # Sample error response from the issue
    error_data = {
        "code": 10000,
        "raw_message": "Banned Prompt: dick",
        "message": "failed to check prompt",
        "detail": None
    }
    
    result_data = {
        "task_id": "6b17484e-93ae-40a0-9a16-014ba1f9cbbc",
        "model": "midjourney",
        "task_type": "imagine",
        "status": "failed",
        "error": error_data
    }
    
    # Test the error parser
    error_message = parse_midjourney_error(error_data)
    print(f"Parsed error message: {error_message}")
    
    expected = '🚫 "dick" is banned prompt by MidJourney, please try another prompt.'
    assert error_message == expected, f"Expected: {expected}, Got: {error_message}"
    
    # Test the full error handler
    user_friendly_message = get_user_friendly_error_message(result_data, "midjourney")
    print(f"User-friendly message: {user_friendly_message}")
    
    assert user_friendly_message == expected, f"Expected: {expected}, Got: {user_friendly_message}"
    
    print("✅ Banned prompt error test passed!")


def test_different_banned_word():
    """Test with a different banned word."""
    print("\nTesting different banned word...")
    
    error_data = {
        "code": 10000,
        "raw_message": "Banned Prompt: nude",
        "message": "failed to check prompt"
    }
    
    result_data = {"error": error_data}
    
    user_friendly_message = get_user_friendly_error_message(result_data, "midjourney")
    print(f"User-friendly message: {user_friendly_message}")
    
    expected = '🚫 "nude" is banned prompt by MidJourney, please try another prompt.'
    assert user_friendly_message == expected, f"Expected: {expected}, Got: {user_friendly_message}"
    
    print("✅ Different banned word test passed!")


def test_no_error():
    """Test that successful responses don't trigger error messages."""
    print("\nTesting successful response...")
    
    result_data = {
        "task_id": "test-task-id", 
        "status": "finished",
        "task_result": {
            "discord_image_url": "https://example.com/image.png"
        }
    }
    
    user_friendly_message = get_user_friendly_error_message(result_data, "midjourney")
    print(f"User-friendly message: {user_friendly_message}")
    
    assert user_friendly_message is None, f"Expected None for successful response, got: {user_friendly_message}"
    
    print("✅ No error test passed!")


if __name__ == "__main__":
    print("🧪 Testing error handling functionality...\n")
    
    try:
        test_midjourney_banned_prompt_error()
        test_different_banned_word()
        test_no_error()
        
        print("\n🎉 All tests passed! Error handling is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise