#!/usr/bin/env python3
"""
Test script for verifying error handling functionality.
"""

import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.error_handler import parse_midjourney_error, get_user_friendly_error_message


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
    
    expected = '"dick" is banned prompt by MidJourney, please try another prompt.'
    assert error_message == expected, f"Expected: {expected}, Got: {error_message}"
    
    # Test the full error handler
    user_friendly_message = get_user_friendly_error_message(result_data, "midjourney")
    print(f"User-friendly message: {user_friendly_message}")
    
    assert user_friendly_message == expected, f"Expected: {expected}, Got: {user_friendly_message}"
    
    print("✅ Banned prompt error test passed!")


def test_generic_midjourney_error():
    """Test handling of generic Midjourney errors."""
    print("\nTesting generic Midjourney error...")
    
    error_data = {
        "code": 10000,
        "raw_message": "Image generation failed due to server error",
        "message": "failed to generate image"
    }
    
    result_data = {
        "task_id": "test-task-id",
        "status": "failed",
        "error": error_data
    }
    
    user_friendly_message = get_user_friendly_error_message(result_data, "midjourney")
    print(f"User-friendly message: {user_friendly_message}")
    
    expected = "🚫 Prompt check failed: Image generation failed due to server error. Please try another prompt."
    assert user_friendly_message == expected, f"Expected: {expected}, Got: {user_friendly_message}"
    
    print("✅ Generic error test passed!")


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
    
    expected = '"nude" is banned prompt by MidJourney, please try another prompt.'
    assert user_friendly_message == expected, f"Expected: {expected}, Got: {user_friendly_message}"
    
    print("✅ Different banned word test passed!")


if __name__ == "__main__":
    print("🧪 Testing error handling functionality...\n")
    
    try:
        test_midjourney_banned_prompt_error()
        test_generic_midjourney_error()
        test_no_error()
        test_different_banned_word()
        
        print("\n🎉 All tests passed! Error handling is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)