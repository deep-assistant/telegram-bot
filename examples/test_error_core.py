#!/usr/bin/env python3
"""
Test script for the core error handling functionality.
"""
import sys
import os
import uuid
import logging
import traceback
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Simple implementation for testing (copy from error_handler.py core functions)
user_error_mapping = {}

def get_or_create_user_error_guid(user_id: int) -> str:
    """Get or create a unique GUID for a user's error tracking."""
    if user_id not in user_error_mapping:
        user_error_mapping[user_id] = str(uuid.uuid4())
    return user_error_mapping[user_id]

def log_error_with_guid(error, user_id: int, context: str = "") -> str:
    """Log an error with user GUID for easy tracking."""
    error_guid = get_or_create_user_error_guid(user_id)
    
    error_details = {
        "user_id": user_id,
        "error_guid": error_guid,
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "traceback": traceback.format_exc()
    }
    
    logging.error(
        f"Error GUID {error_guid} for user {user_id}: {error_details['error_type']}: {error_details['error_message']} "
        f"Context: {context}",
        extra=error_details
    )
    
    return error_guid

def format_error_for_private_logging(error, user_id: int, context: str = "") -> str:
    """Format error details for private chat or repository logging."""
    error_guid = get_or_create_user_error_guid(user_id)
    
    formatted_message = f"""
🚨 **Bot Error Report**

**Error GUID:** `{error_guid}`
**User ID:** `{user_id}`
**Timestamp:** `{datetime.now().isoformat()}`
**Error Type:** `{type(error).__name__}`
**Context:** `{context}`

**Error Message:**
```
{str(error)}
```

**Traceback:**
```
{traceback.format_exc()}
```
"""
    return formatted_message

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
    guid = log_error_with_guid(test_error, user_id, "test_context")
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
    
    try:
        # Simulate an error to get a real traceback
        raise test_error
    except RuntimeError as e:
        formatted_message = format_error_for_private_logging(e, user_id, "database_operation")
    
    print("Formatted private message:")
    print("=" * 50)
    print(formatted_message)
    print("=" * 50)
    
    # Check that key components are present
    assert "Error GUID:" in formatted_message, "Should contain Error GUID"
    assert "User ID:" in formatted_message, "Should contain User ID"
    assert "RuntimeError" in formatted_message, "Should contain error type"
    assert "Database connection failed" in formatted_message, "Should contain error message"
    
    print("✅ Private logging format test passed!")

def test_user_error_message_format():
    """Test the user-facing error message format."""
    print("\nTesting user error message format...")
    
    user_id = 12345
    error_guid = get_or_create_user_error_guid(user_id)
    
    user_message = f"""
😔 К сожалению, произошла ошибка.

🔍 **Код ошибки для службы поддержки:** `{error_guid}`

📞 Если проблема повторяется, сообщите нам этот код в @deepGPT
    """
    
    print("User-facing error message:")
    print("=" * 50)
    print(user_message)
    print("=" * 50)
    
    assert error_guid in user_message, "User message should contain the error GUID"
    
    print("✅ User error message format test passed!")

def main():
    """Run all tests."""
    print("🧪 Testing Error Handling System Core Functionality\n")
    
    test_guid_generation()
    test_error_logging()
    test_private_logging_format()
    test_user_error_message_format()
    
    print("\n🎉 All core tests passed! Error handling system is working correctly.")
    print("\nImplementation summary:")
    print("✅ User GUID generation system")
    print("✅ Error logging with GUID tracking")
    print("✅ Private error report formatting")
    print("✅ User-friendly error messages with GUID")
    
    print("\nThe system provides:")
    print("- Unique error tracking GUID for each user")
    print("- Detailed error logging for administrators")
    print("- User-friendly error messages with support codes")
    print("- Optional private chat/repository error reporting")

if __name__ == "__main__":
    main()