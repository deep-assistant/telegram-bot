import logging
import traceback
from datetime import datetime, timezone
from typing import List, Optional
import json
import os

from aiogram import Bot
from aiogram.types import TelegramObject, Message, CallbackQuery

import config


class ErrorReportingService:
    """Service for reporting and managing errors"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.admin_user_ids = self._get_admin_user_ids()
        self.error_log_file = "error_reports.jsonl"
    
    def _get_admin_user_ids(self) -> List[int]:
        """Get list of admin user IDs from config or environment"""
        # Try to get from config first, then environment
        admin_ids_str = getattr(config, 'ADMIN_USER_IDS', '') or os.getenv('ADMIN_USER_IDS', '')
        
        if not admin_ids_str:
            return []
        
        try:
            return [int(uid.strip()) for uid in admin_ids_str.split(',') if uid.strip()]
        except ValueError:
            self.logger.warning("Invalid ADMIN_USER_IDS format. Should be comma-separated integers.")
            return []
    
    async def report_error(
        self, 
        exception: Exception, 
        context: dict, 
        event: Optional[TelegramObject] = None
    ) -> None:
        """Report an error to administrators and log it"""
        
        # Create error report
        error_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc(),
            'context': context
        }
        
        # Log to file
        await self._log_error_to_file(error_report)
        
        # Send notifications to admins
        if self.admin_user_ids and hasattr(event, 'bot'):
            await self._notify_admins(event.bot, error_report)
    
    async def _log_error_to_file(self, error_report: dict) -> None:
        """Log error report to file"""
        try:
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_report, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write error to file: {e}")
    
    async def _notify_admins(self, bot: Bot, error_report: dict) -> None:
        """Send error notifications to administrators"""
        if not self.admin_user_ids:
            return
        
        # Format error message
        message = self._format_error_message(error_report)
        
        # Send to each admin
        for admin_id in self.admin_user_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Failed to send error report to admin {admin_id}: {e}")
    
    def _format_error_message(self, error_report: dict) -> str:
        """Format error report for Telegram message"""
        context = error_report['context']
        
        lines = [
            "🚨 **Ошибка в боте**",
            "",
            f"**Время:** `{error_report['timestamp']}`",
            f"**Тип ошибки:** `{error_report['exception_type']}`",
            f"**Сообщение:** `{error_report['exception_message']}`",
            "",
            "**Контекст:**"
        ]
        
        # Add context information
        if context.get('user_id'):
            lines.append(f"• Пользователь: `{context['user_id']}`")
        if context.get('username'):
            lines.append(f"• Username: `@{context['username']}`")
        if context.get('chat_id'):
            lines.append(f"• Чат: `{context['chat_id']}` ({context.get('chat_type', 'unknown')})")
        if context.get('text'):
            lines.append(f"• Текст: `{context['text']}`")
        if context.get('callback_data'):
            lines.append(f"• Callback data: `{context['callback_data']}`")
        
        # Add truncated traceback (last few lines)
        traceback_lines = error_report['traceback'].split('\n')
        if len(traceback_lines) > 5:
            lines.extend([
                "",
                "**Трассировка (последние строки):**",
                f"```\n{''.join(traceback_lines[-5:])}\n```"
            ])
        else:
            lines.extend([
                "",
                "**Трассировка:**",
                f"```\n{error_report['traceback']}\n```"
            ])
        
        message = '\n'.join(lines)
        
        # Telegram message limit is 4096 characters
        if len(message) > 4000:
            message = message[:4000] + "\n...\n*(сообщение обрезано)*"
        
        return message
    
    async def get_recent_errors(self, limit: int = 10) -> List[dict]:
        """Get recent error reports"""
        try:
            if not os.path.exists(self.error_log_file):
                return []
            
            with open(self.error_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get last 'limit' lines and parse JSON
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            errors = []
            
            for line in recent_lines:
                try:
                    errors.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            
            return errors[::-1]  # Return in reverse order (newest first)
        
        except Exception as e:
            self.logger.error(f"Failed to read error log: {e}")
            return []
    
    async def clear_error_log(self) -> bool:
        """Clear the error log file"""
        try:
            if os.path.exists(self.error_log_file):
                os.remove(self.error_log_file)
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear error log: {e}")
            return False