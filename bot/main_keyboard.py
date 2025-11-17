from typing import Union
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery

from bot.commands import change_model_text, change_system_message_text, balance_text 
from bot.commands import clear_text, get_history_text, images_command_text
from bot.commands import referral_command_text, suno_text, balance_payment_command_text
from bot.commands import transfer_text

# Dictionary to track message counts per chat since bot startup
chat_message_counts = {}

# Configurable number of first messages to include the keyboard
FIRST_MESSAGES_LIMIT = 3

def create_main_keyboard():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text=balance_text()),
                KeyboardButton(text=balance_payment_command_text())
            ],
            [
                KeyboardButton(text=change_model_text()),
                KeyboardButton(text=change_system_message_text())
            ],
            [
                KeyboardButton(text=suno_text()),
                KeyboardButton(text=images_command_text())
            ],
            [
                KeyboardButton(text=clear_text()),
                KeyboardButton(text=get_history_text())
            ],
            [
                KeyboardButton(text=referral_command_text()),
                KeyboardButton(text=transfer_text())
            ],
        ],
        input_field_placeholder="💬 Задай свой вопрос"
    )

async def send_message(callback_or_message: Union[Message, CallbackQuery], *args, **kwargs):
    """
    Sends a message with all provided args and kwargs, supporting both Message and CallbackQuery.
    If reply_markup is not provided and this is one of the first 3 messages in the chat,
    adds the main keyboard from create_main_keyboard().
    """
    # Determine the type and extract chat ID and response method
    if isinstance(callback_or_message, Message):
        chat_id = callback_or_message.chat.id
        responder = callback_or_message.answer
    elif isinstance(callback_or_message, CallbackQuery):
        chat_id = callback_or_message.message.chat.id
        responder = callback_or_message.message.answer
    else:
        raise ValueError("First argument must be Message or CallbackQuery")

    # Initialize message count for this chat if not already present
    if chat_id not in chat_message_counts:
        chat_message_counts[chat_id] = 0
    
    # Increment the message count for this chat
    chat_message_counts[chat_id] += 1

    # Check if reply_markup is in kwargs and if we're within the first 3 messages
    if 'reply_markup' not in kwargs and chat_message_counts[chat_id] <= FIRST_MESSAGES_LIMIT:
        kwargs['reply_markup'] = create_main_keyboard()

    # Send the message with all provided args and kwargs
    await responder(*args, **kwargs)