import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from db import data_base, db_key


class MultiModeMessage:
    def __init__(self, text: str, timestamp: datetime):
        self.text = text
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiModeMessage':
        return cls(
            text=data["text"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class MultiModeService:
    MESSAGES_KEY = "multi_mode_messages"
    AUTO_CONFIRM_TIMER_KEY = "multi_mode_auto_timer"
    AUTO_CONFIRM_SECONDS_KEY = "multi_mode_auto_seconds"
    
    def add_message(self, user_id: str, text: str) -> None:
        """Add a message to the user's multi-mode batch"""
        message = MultiModeMessage(text, datetime.now())
        
        messages = self.get_messages(user_id)
        messages.append(message)
        
        self._save_messages(user_id, messages)
    
    def get_messages(self, user_id: str) -> List[MultiModeMessage]:
        """Get all batched messages for a user"""
        try:
            key = db_key(user_id, self.MESSAGES_KEY)
            data = data_base[key].decode('utf-8')
            messages_data = json.loads(data)
            return [MultiModeMessage.from_dict(msg) for msg in messages_data]
        except KeyError:
            return []
    
    def clear_messages(self, user_id: str) -> None:
        """Clear all batched messages for a user"""
        key = db_key(user_id, self.MESSAGES_KEY)
        try:
            with data_base.transaction():
                del data_base[key]
            data_base.commit()
        except KeyError:
            pass
    
    def get_combined_text(self, user_id: str) -> str:
        """Get all messages combined into a single text"""
        messages = self.get_messages(user_id)
        if not messages:
            return ""
        
        combined_parts = []
        for i, message in enumerate(messages, 1):
            combined_parts.append(f"Сообщение {i}: {message.text}")
        
        return "\n\n".join(combined_parts)
    
    def get_message_count(self, user_id: str) -> int:
        """Get the number of batched messages for a user"""
        return len(self.get_messages(user_id))
    
    def set_auto_confirm_seconds(self, user_id: str, seconds: int) -> None:
        """Set auto-confirmation timer in seconds for a user"""
        key = db_key(user_id, self.AUTO_CONFIRM_SECONDS_KEY)
        with data_base.transaction():
            data_base[key] = str(seconds)
        data_base.commit()
    
    def get_auto_confirm_seconds(self, user_id: str) -> Optional[int]:
        """Get auto-confirmation timer in seconds for a user"""
        try:
            key = db_key(user_id, self.AUTO_CONFIRM_SECONDS_KEY)
            return int(data_base[key].decode('utf-8'))
        except (KeyError, ValueError):
            return None
    
    def clear_auto_confirm_seconds(self, user_id: str) -> None:
        """Clear auto-confirmation timer for a user"""
        key = db_key(user_id, self.AUTO_CONFIRM_SECONDS_KEY)
        try:
            with data_base.transaction():
                del data_base[key]
            data_base.commit()
        except KeyError:
            pass
    
    def _save_messages(self, user_id: str, messages: List[MultiModeMessage]) -> None:
        """Save messages to database"""
        key = db_key(user_id, self.MESSAGES_KEY)
        messages_data = [msg.to_dict() for msg in messages]
        
        with data_base.transaction():
            data_base[key] = json.dumps(messages_data)
        data_base.commit()


multiModeService = MultiModeService()