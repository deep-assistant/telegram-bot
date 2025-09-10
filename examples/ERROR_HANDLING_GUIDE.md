# Error Handling with User GUID System

This guide explains how to use the error handling system that provides unique error tracking GUIDs to users.

## Overview

The error handling system solves the problem described in issue #69: when users encounter errors, they now receive a unique GUID that administrators can use to find the specific error in logs.

## Features

- **User GUID Generation**: Each user gets a unique GUID for error tracking
- **Detailed Error Logging**: Errors are logged with context and full tracebacks
- **User-Friendly Messages**: Users receive error messages with their unique GUID
- **Private Error Reporting**: Optional integration with Telegram chats or GitHub issues

## Usage

### Basic Error Handling

```python
from bot.error_handler import send_error_message_with_guid

async def your_handler(message: Message):
    try:
        # Your code that might fail
        result = await some_risky_operation()
    except Exception as e:
        # Send error message with GUID to user and log details
        await send_error_message_with_guid(message, e, "your_handler_context")
        return
```

### Manual Error Logging

```python
from bot.error_handler import log_error_with_guid, get_or_create_user_error_guid

async def your_handler(message: Message):
    user_id = message.from_user.id
    
    try:
        # Your code
        pass
    except Exception as e:
        # Just log the error and get GUID, don't send to user
        error_guid = log_error_with_guid(e, user_id, "silent_operation")
        
        # Handle error differently
        await message.answer(f"Operation failed. Error ID: {error_guid}")
```

## Configuration

Add these settings to your `config.py`:

```python
# Error Logging Configuration
ERROR_LOGGING_ENABLED = True  # Enable private error reporting
ERROR_LOGGING_CHAT_ID = "123456789"  # Your private chat/channel ID
ERROR_LOGGING_GITHUB_REPO = "owner/repo"  # Optional: GitHub repo for issues
ERROR_LOGGING_GITHUB_TOKEN = "ghp_xxxxx"  # Optional: GitHub token
```

## Error Message Format

Users receive messages like this:

```
😔 К сожалению, произошла ошибка.

🔍 Код ошибки для службы поддержки: a1b2c3d4-e5f6-7890-abcd-ef1234567890

📞 Если проблема повторяется, сообщите нам этот код в @deepGPT
```

## Private Error Reports

When enabled, administrators receive detailed reports:

```
🚨 Bot Error Report

Error GUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
User ID: 123456789
Timestamp: 2025-09-11T01:02:52.032224
Error Type: RuntimeError
Context: handle_gpt_request

Error Message:
Database connection failed

Traceback:
Traceback (most recent call last):
  File "bot/gpt/router.py", line 129, in handle_gpt_request
    answer = await completionsService.query_chatgpt(...)
RuntimeError: Database connection failed
```

## Implementation Status

Currently implemented in:
- `bot/gpt/router.py` - Main GPT request handling
- `bot/gpt/router.py` - Document processing
- `bot/gpt/router.py` - Dialog context clearing

The same pattern can be applied to other routers by:
1. Importing `from bot.error_handler import send_error_message_with_guid`
2. Replacing basic `except Exception as e:` handlers with calls to `send_error_message_with_guid`

## Benefits

1. **Faster Support**: Users provide specific error codes instead of vague descriptions
2. **Better Debugging**: Administrators can quickly find exact error details in logs
3. **User Experience**: Users know their error was logged and can reference it
4. **Monitoring**: Optional integration with private chats or GitHub for error tracking

## Testing

Run the test script to verify functionality:

```bash
python3 examples/test_error_core.py
```

This will test GUID generation, error logging, and message formatting.