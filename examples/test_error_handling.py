#!/usr/bin/env python3
"""
Test script for the error handling system with GUID generation.
"""
import sys
import os
import asyncio
import logging

# Add bot directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot.error_handler import (
    get_or_create_user_error_guid, 
    log_error_with_guid,
    format_error_for_private_logging
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_guid_generation():
    """Test GUID generation and consistency."""
    print("Testing GUID generation...")
    
    user_id = 12345
    
    # First call should create a new GUID
    guid1 = get_or_create_user_error_guid(user_id)
    print(f"First GUID for user {user_id}: {guid1}")
    
    # Second call should return the same GUID
    guid2 = get_or_create_user_error_guid(user_id)
    print(f"Second GUID for user {user_id}: {guid2}")
    
    assert guid1 == guid2, "GUIDs should be consistent for the same user"
    
    # Different user should get different GUID
    user_id2 = 67890
    guid3 = get_or_create_user_error_guid(user_id2)
    print(f"GUID for user {user_id2}: {guid3}")
    
    assert guid1 != guid3, "Different users should get different GUIDs"
    
    print("✅ GUID generation test passed!")

def test_error_logging():
    """Test error logging with GUID."""
    print("\nTesting error logging...")
    
    user_id = 12345
    test_error = ValueError("Test error for demonstration")
    
    # Log the error
    guid = log_error_with_guid(test_error, user_id, "test_context", {"extra": "data"})
    print(f"Logged error with GUID: {guid}")
    
    # Should be the same as before for the same user
    existing_guid = get_or_create_user_error_guid(user_id)
    assert guid == existing_guid, "Error GUID should match user GUID"
    
    print("✅ Error logging test passed!")

def test_private_logging_format():
    """Test private logging message formatting."""
    print("\nTesting private logging format...")
    
    user_id = 12345
    test_error = RuntimeError("Database connection failed")
    
    formatted_message = format_error_for_private_logging(
        test_error, 
        user_id, 
        "database_operation",
        {"query": "SELECT * FROM users", "attempt": 3}
    )
    
    print("Formatted private message:")
    print(formatted_message)
    
    # Check that key components are present
    assert "Error GUID:" in formatted_message, "Should contain Error GUID"
    assert "User ID:" in formatted_message, "Should contain User ID"
    assert "RuntimeError" in formatted_message, "Should contain error type"
    assert "Database connection failed" in formatted_message, "Should contain error message"
    
    print("✅ Private logging format test passed!")

def main():
    """Run all tests."""
    print("🧪 Testing Error Handling System\n")
    
    test_guid_generation()
    test_error_logging()
    test_private_logging_format()
    
    print("\n🎉 All tests passed! Error handling system is working correctly.")
    print("\nTo use the system in your bot:")
    print("1. Import: from bot.error_handler import send_error_message_with_guid")
    print("2. In exception handlers: await send_error_message_with_guid(message, exception, 'context')")
    print("3. Configure error reporting in config.py if needed")

if __name__ == "__main__":
    main()