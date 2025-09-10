import asyncio
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

import config
from .service import ErrorReportingService


class ErrorReportingMiddleware(BaseMiddleware):
    """Middleware to capture and report unhandled exceptions"""
    
    def __init__(self):
        self.error_service = ErrorReportingService()
        self.logger = logging.getLogger(__name__)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            # Log the error
            self.logger.error(f"Unhandled exception: {e}", exc_info=True)
            
            # Get context information
            context = self._extract_context(event)
            
            # Report the error
            try:
                await self.error_service.report_error(
                    exception=e,
                    context=context,
                    event=event
                )
            except Exception as report_error:
                # Fallback logging if error reporting itself fails
                self.logger.error(f"Failed to report error: {report_error}", exc_info=True)
            
            # Try to send user-friendly message
            if isinstance(event, (Message, CallbackQuery)):
                try:
                    if isinstance(event, Message):
                        await event.answer("❌ Произошла ошибка. Администратор был уведомлен.")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("❌ Произошла ошибка. Администратор был уведомлен.", show_alert=True)
                except Exception:
                    pass  # Silently ignore if we can't send user message
            
            # Re-raise the exception to prevent the application from continuing with broken state
            if config.IS_DEV:
                raise
    
    def _extract_context(self, event: TelegramObject) -> dict:
        """Extract relevant context from the event"""
        context = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': type(event).__name__
        }
        
        if isinstance(event, Message):
            context.update({
                'message_id': event.message_id,
                'chat_id': event.chat.id,
                'chat_type': event.chat.type,
                'user_id': event.from_user.id if event.from_user else None,
                'username': event.from_user.username if event.from_user else None,
                'text': event.text[:100] if event.text else None,  # First 100 chars
                'content_type': event.content_type
            })
        elif isinstance(event, CallbackQuery):
            context.update({
                'callback_id': event.id,
                'data': event.data,
                'user_id': event.from_user.id if event.from_user else None,
                'username': event.from_user.username if event.from_user else None
            })
            if event.message:
                context.update({
                    'message_id': event.message.message_id,
                    'chat_id': event.message.chat.id,
                    'chat_type': event.message.chat.type
                })
        
        return context