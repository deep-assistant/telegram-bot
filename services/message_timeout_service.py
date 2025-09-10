import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Set
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

import config


class MessageTimeoutService:
    """Service to handle automatic deletion of user messages after a timeout period."""
    
    def __init__(self):
        self.scheduled_deletions: Dict[str, asyncio.Task] = {}
        self.processed_messages: Set[str] = set()
        
    def _get_message_key(self, chat_id: int, message_id: int) -> str:
        """Generate a unique key for a message."""
        return f"{chat_id}:{message_id}"
    
    async def _delete_message_after_timeout(self, bot: Bot, chat_id: int, message_id: int, timeout_seconds: int):
        """Delete a message after the specified timeout."""
        try:
            await asyncio.sleep(timeout_seconds)
            
            # Check if message was already processed (replied to, etc.)
            message_key = self._get_message_key(chat_id, message_id)
            if message_key in self.processed_messages:
                logging.info(f"Message {message_key} already processed, skipping deletion")
                return
            
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            logging.info(f"Deleted message {message_id} from chat {chat_id} after timeout")
            
        except TelegramBadRequest as e:
            if "message to delete not found" in str(e).lower():
                logging.info(f"Message {message_id} in chat {chat_id} already deleted")
            else:
                logging.error(f"Failed to delete message {message_id} in chat {chat_id}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error deleting message {message_id} in chat {chat_id}: {e}")
        finally:
            # Clean up the task reference
            message_key = self._get_message_key(chat_id, message_id)
            self.scheduled_deletions.pop(message_key, None)
    
    def schedule_message_deletion(self, bot: Bot, chat_id: int, message_id: int, timeout_seconds: int = None):
        """Schedule a message for deletion after the timeout period."""
        if not config.MESSAGE_TIMEOUT_ENABLED:
            return
        
        if timeout_seconds is None:
            timeout_seconds = config.MESSAGE_TIMEOUT_SECONDS
        
        if timeout_seconds <= 0:
            return
        
        message_key = self._get_message_key(chat_id, message_id)
        
        # Cancel any existing deletion task for this message
        if message_key in self.scheduled_deletions:
            self.scheduled_deletions[message_key].cancel()
        
        # Schedule the new deletion task
        task = asyncio.create_task(
            self._delete_message_after_timeout(bot, chat_id, message_id, timeout_seconds)
        )
        self.scheduled_deletions[message_key] = task
        
        logging.info(f"Scheduled deletion of message {message_id} in chat {chat_id} after {timeout_seconds} seconds")
    
    def cancel_message_deletion(self, chat_id: int, message_id: int):
        """Cancel the scheduled deletion of a message."""
        message_key = self._get_message_key(chat_id, message_id)
        
        if message_key in self.scheduled_deletions:
            self.scheduled_deletions[message_key].cancel()
            del self.scheduled_deletions[message_key]
            logging.info(f"Cancelled scheduled deletion of message {message_id} in chat {chat_id}")
    
    def mark_message_processed(self, chat_id: int, message_id: int):
        """Mark a message as processed (replied to, handled, etc.) to prevent deletion."""
        message_key = self._get_message_key(chat_id, message_id)
        self.processed_messages.add(message_key)
        
        # Also cancel any scheduled deletion since the message was processed
        self.cancel_message_deletion(chat_id, message_id)
        
        logging.info(f"Marked message {message_id} in chat {chat_id} as processed")
    
    def cleanup_old_processed_messages(self, max_age_hours: int = 24):
        """Clean up old processed message records to prevent memory leaks."""
        # Since we only store message keys and don't track timestamps,
        # we'll periodically clear the entire set to prevent unbounded growth
        if len(self.processed_messages) > 10000:  # Arbitrary threshold
            self.processed_messages.clear()
            logging.info("Cleared processed messages cache due to size limit")


# Global instance
message_timeout_service = MessageTimeoutService()