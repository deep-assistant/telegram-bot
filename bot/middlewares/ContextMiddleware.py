import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from services import contextService, tokenizeService


class ContextMiddleware(BaseMiddleware):
    """Middleware to track user interactions and show context notifications"""
    
    async def __call__(self, handler, event: Message, data):
        # Only process message events from users (not system messages)
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)
        
        user_id = str(event.from_user.id)
        
        # Check if we should show context notification before processing the message
        if contextService.should_show_context_notification(user_id):
            await self.show_context_notification(event, user_id)
            return  # Don't process the original message, wait for user choice
        
        # Update last interaction timestamp for this user
        contextService.update_last_interaction(user_id)
        
        # Continue with normal message processing
        return await handler(event, data)
    
    async def show_context_notification(self, message: Message, user_id: str):
        """Show context notification with clear/keep options"""
        # Mark that we've sent the notification
        contextService.set_notification_sent(user_id)
        
        # Check if user has any context/history
        history = await tokenizeService.history(user_id)
        
        # If no history exists, just update interaction and continue normally
        if history is None or history.get("status") == 404:
            contextService.update_last_interaction(user_id)
            return
        
        notification_text = """
🕰 Вы не общались с ботом более суток.

У вас есть предыдущий контекст диалога, который может увеличить расходы на обработку сообщений.

Что вы хотите сделать?
"""
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🗑 Очистить контекст", 
                        callback_data=f"context_clear_{user_id}"
                    ),
                    InlineKeyboardButton(
                        text="📝 Оставить контекст", 
                        callback_data=f"context_keep_{user_id}"
                    )
                ]
            ]
        )
        
        # Store the original message text so we can process it after user chooses
        from db import data_base
        original_message_key = f"pending_message_{user_id}"
        with data_base.transaction():
            data_base[original_message_key] = message.text or ""
        data_base.commit()
        
        await message.answer(notification_text, reply_markup=keyboard)