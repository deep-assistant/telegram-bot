from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.gpt.command_types import change_model_text, change_system_message_text, balance_text, clear_text, \
    get_history_text
from bot.images import images_command_text
from bot.payment.command_types import balance_payment_command_text
from bot.referral import referral_command_text
from bot.suno.command_types import suno_text

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
            ],
        ],
        input_field_placeholder="💬 Задай свой вопрос"
    )

