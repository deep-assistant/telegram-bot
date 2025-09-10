from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from services import stateService, StateTypes


class PromptEditingMiddleware(BaseMiddleware):
    """
    Middleware to skip all routes when user is in prompt editing mode.
    This ensures that when editing system messages, other commands are ignored.
    Includes timeout-based safety mechanism.
    """

    async def __call__(self, handler, event, data):
        # Only process message events, let other events pass through
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
        
        # Get user_id from the event
        user_id = event.from_user.id
        
        # Check and handle timeout first
        timeout_occurred = stateService.check_and_handle_editing_timeout(user_id)
        
        if timeout_occurred:
            # If timeout occurred, notify user and let the message be processed normally
            if isinstance(event, Message):
                await event.answer("⚠️ Время редактирования системного сообщения истекло. Режим редактирования отключен.")
            return await handler(event, data)
        
        # Check if user is in system message editing mode
        if stateService.is_system_message_editing_state(user_id):
            # Only allow processing if this is the SystemMessageEditing handler or cancel callback
            # Check if this is a cancel callback
            if isinstance(event, CallbackQuery) and event.data and event.data.startswith("cancel-system-edit"):
                return await handler(event, data)
            
            # Check if this is a message and we're targeting the SystemMessageEditing state
            if isinstance(event, Message):
                # Allow the message to be processed by the SystemMessageEditing handler
                # The StateCommand filter will ensure only the right handler processes it
                return await handler(event, data)
            
            # For all other callback queries in editing mode, ignore them
            if isinstance(event, CallbackQuery):
                await event.answer("Вы находитесь в режиме редактирования системного сообщения. Отправьте новое сообщение или отмените редактирование.")
                return
        
        # If not in editing mode, process normally
        return await handler(event, data)