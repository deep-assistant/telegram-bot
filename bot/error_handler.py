"""
Error handling utilities with user GUID generation for error tracking.
"""
import uuid
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from aiogram.types import Message
from .error_reporter import get_error_reporter

# Store to map user_id to error_guid for the session
user_error_mapping: Dict[int, str] = {}

def get_or_create_user_error_guid(user_id: int) -> str:
    """
    Get or create a unique GUID for a user's error tracking.
    This GUID helps correlate user errors with logs.
    
    Args:
        user_id (int): Telegram user ID
        
    Returns:
        str: User's error tracking GUID
    """
    if user_id not in user_error_mapping:
        user_error_mapping[user_id] = str(uuid.uuid4())
    
    return user_error_mapping[user_id]

def log_error_with_guid(
    error: Exception, 
    user_id: int, 
    context: str = "", 
    extra_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Log an error with user GUID for easy tracking.
    
    Args:
        error (Exception): The exception that occurred
        user_id (int): Telegram user ID
        context (str): Additional context about where the error occurred
        extra_data (dict): Additional data to log
        
    Returns:
        str: The user's error GUID for display
    """
    error_guid = get_or_create_user_error_guid(user_id)
    
    # Create detailed error log entry
    error_details = {
        "user_id": user_id,
        "error_guid": error_guid,
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "traceback": traceback.format_exc()
    }
    
    if extra_data:
        error_details.update(extra_data)
    
    # Log the error with all details
    logging.error(
        f"Error GUID {error_guid} for user {user_id}: {error_details['error_type']}: {error_details['error_message']} "
        f"Context: {context}",
        extra=error_details
    )
    
    return error_guid

async def send_error_message_with_guid(
    message: Message, 
    error: Exception, 
    context: str = "",
    report_to_private: bool = True
) -> None:
    """
    Send an error message to the user with their error GUID for support purposes.
    
    Args:
        message (Message): The Telegram message object
        error (Exception): The exception that occurred
        context (str): Additional context about the error
        report_to_private (bool): Whether to send error report to private channels
    """
    user_id = message.from_user.id
    error_guid = log_error_with_guid(error, user_id, context)
    
    error_message = f"""
😔 К сожалению, произошла ошибка.

🔍 **Код ошибки для службы поддержки:** `{error_guid}`

📞 Если проблема повторяется, сообщите нам этот код в @deepGPT
    """
    
    try:
        await message.answer(error_message)
    except Exception as send_error:
        # If we can't send the message, at least log it
        logging.error(f"Failed to send error message to user {user_id}: {send_error}")
    
    # Send error report to private channels if enabled
    if report_to_private:
        try:
            error_reporter = get_error_reporter(message.bot)
            private_error_message = format_error_for_private_logging(
                error, user_id, context, {"message_text": message.text[:500] if message.text else None}
            )
            await error_reporter.report_error(private_error_message, error_guid)
        except Exception as report_error:
            logging.error(f"Failed to send error report to private channels: {report_error}")

def format_error_for_private_logging(
    error: Exception, 
    user_id: int, 
    context: str = "",
    extra_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format error details for private chat or repository logging.
    
    Args:
        error (Exception): The exception that occurred
        user_id (int): Telegram user ID
        context (str): Additional context about the error
        extra_data (dict): Additional data to include
        
    Returns:
        str: Formatted error message for private logging
    """
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
    
    if extra_data:
        formatted_message += f"\n**Additional Data:**\n```json\n{extra_data}\n```"
    
    return formatted_message