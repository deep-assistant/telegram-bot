import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from db import data_base, db_key


@dataclass
class Reminder:
    id: str
    user_id: int
    chat_id: int
    message: str
    trigger_time: datetime
    created_at: datetime
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'message': self.message,
            'trigger_time': self.trigger_time.isoformat(),
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reminder':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            chat_id=data['chat_id'],
            message=data['message'],
            trigger_time=datetime.fromisoformat(data['trigger_time']),
            created_at=datetime.fromisoformat(data['created_at']),
            is_active=data.get('is_active', True)
        )


class ReminderService:
    REMINDERS_KEY = "reminders"
    NEXT_ID_KEY = "next_reminder_id"

    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Task] = {}

    def _get_next_id(self) -> int:
        try:
            next_id = int(data_base[self.NEXT_ID_KEY].decode('utf-8'))
        except KeyError:
            next_id = 1
        
        with data_base.transaction():
            data_base[self.NEXT_ID_KEY] = str(next_id + 1)
        data_base.commit()
        
        return next_id

    def _get_user_reminders_key(self, user_id: int) -> str:
        return db_key(user_id, self.REMINDERS_KEY)

    def _save_reminder(self, reminder: Reminder) -> None:
        key = self._get_user_reminders_key(reminder.user_id)
        
        try:
            reminders_data = json.loads(data_base[key].decode('utf-8'))
        except KeyError:
            reminders_data = {}
        
        reminders_data[reminder.id] = reminder.to_dict()
        
        with data_base.transaction():
            data_base[key] = json.dumps(reminders_data)
        data_base.commit()

    def _delete_reminder(self, user_id: int, reminder_id: str) -> None:
        key = self._get_user_reminders_key(user_id)
        
        try:
            reminders_data = json.loads(data_base[key].decode('utf-8'))
            if reminder_id in reminders_data:
                del reminders_data[reminder_id]
                
                with data_base.transaction():
                    data_base[key] = json.dumps(reminders_data)
                data_base.commit()
        except KeyError:
            pass

    def get_user_reminders(self, user_id: int) -> List[Reminder]:
        key = self._get_user_reminders_key(user_id)
        
        try:
            reminders_data = json.loads(data_base[key].decode('utf-8'))
            reminders = []
            
            for reminder_dict in reminders_data.values():
                reminder = Reminder.from_dict(reminder_dict)
                if reminder.is_active and reminder.trigger_time > datetime.now():
                    reminders.append(reminder)
            
            return sorted(reminders, key=lambda r: r.trigger_time)
        except KeyError:
            return []

    def parse_time_expression(self, text: str) -> Optional[timedelta]:
        patterns = [
            (r'через\s+(\d+)\s+(?:минут[уыа]?|мин)', lambda m: timedelta(minutes=int(m.group(1)))),
            (r'через\s+(\d+)\s+(?:час[ова]?)', lambda m: timedelta(hours=int(m.group(1)))),
            (r'через\s+(\d+)\s+(?:день|дня|дней)', lambda m: timedelta(days=int(m.group(1)))),
            (r'через\s+(\d+)\s+(?:недел[юия])', lambda m: timedelta(weeks=int(m.group(1)))),
            (r'через\s+(\d+)\s+(?:секунд[уыа]?|сек)', lambda m: timedelta(seconds=int(m.group(1)))),
        ]
        
        text_lower = text.lower()
        
        for pattern, delta_func in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return delta_func(match)
        
        return None

    def extract_reminder_message(self, text: str) -> str:
        parts = text.split('"', 2)
        if len(parts) >= 2:
            return parts[1]
        
        parts = text.split("'", 2)
        if len(parts) >= 2:
            return parts[1]
        
        time_match = re.search(r'через\s+\d+\s+(?:минут[уыа]?|час[ова]?|день|дня|дней|недел[юия]|секунд[уыа]?|мин|сек)', text.lower())
        if time_match:
            return text[time_match.end():].strip()
        
        return text.replace('/remind', '').strip()

    async def create_reminder(self, user_id: int, chat_id: int, text: str, bot) -> Optional[Reminder]:
        time_delta = self.parse_time_expression(text)
        if not time_delta:
            return None
        
        message = self.extract_reminder_message(text)
        if not message:
            message = "Напоминание"
        
        reminder_id = str(self._get_next_id())
        now = datetime.now()
        trigger_time = now + time_delta
        
        reminder = Reminder(
            id=reminder_id,
            user_id=user_id,
            chat_id=chat_id,
            message=message,
            trigger_time=trigger_time,
            created_at=now
        )
        
        self._save_reminder(reminder)
        
        await self._schedule_reminder(reminder, bot)
        
        return reminder

    async def _schedule_reminder(self, reminder: Reminder, bot) -> None:
        async def send_reminder():
            try:
                delay = (reminder.trigger_time - datetime.now()).total_seconds()
                if delay > 0:
                    await asyncio.sleep(delay)
                
                if reminder.id in self.active_tasks:
                    await bot.send_message(
                        chat_id=reminder.chat_id,
                        text=f"🔔 Напоминание: {reminder.message}"
                    )
                    
                    self._delete_reminder(reminder.user_id, reminder.id)
                    
                    if reminder.id in self.active_tasks:
                        del self.active_tasks[reminder.id]
                        
            except Exception as e:
                print(f"Error sending reminder {reminder.id}: {e}")
                if reminder.id in self.active_tasks:
                    del self.active_tasks[reminder.id]
        
        task = asyncio.create_task(send_reminder())
        self.active_tasks[reminder.id] = task

    def cancel_reminder(self, user_id: int, reminder_id: str) -> bool:
        reminders = self.get_user_reminders(user_id)
        reminder = next((r for r in reminders if r.id == reminder_id), None)
        
        if reminder:
            if reminder_id in self.active_tasks:
                self.active_tasks[reminder_id].cancel()
                del self.active_tasks[reminder_id]
            
            self._delete_reminder(user_id, reminder_id)
            return True
        
        return False

    async def restore_reminders(self, bot) -> None:
        all_keys = []
        try:
            cursor = data_base.iterator()
            for key in cursor:
                key_str = key.decode('utf-8')
                if key_str.endswith('_reminders'):
                    all_keys.append(key_str)
        except Exception as e:
            print(f"Error iterating database keys: {e}")
            return
        
        for key in all_keys:
            try:
                reminders_data = json.loads(data_base[key].decode('utf-8'))
                
                for reminder_dict in reminders_data.values():
                    reminder = Reminder.from_dict(reminder_dict)
                    
                    if (reminder.is_active and 
                        reminder.trigger_time > datetime.now() and 
                        reminder.id not in self.active_tasks):
                        
                        await self._schedule_reminder(reminder, bot)
                        
            except Exception as e:
                print(f"Error restoring reminders from {key}: {e}")


reminderService = ReminderService()