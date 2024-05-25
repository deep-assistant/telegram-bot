from aiogram import types, Router
from aiogram.filters import CommandStart

from bot.gpt.command_types import change_model_text, change_system_message_text
from bot.payment.command_types import payment_command_text

startRouter = Router()

hello_text = """
👋 Привет! Я самый умный бот, я использую в себе самые мощные нейросети на данный момент!

🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение! 
"""


@startRouter.message(CommandStart())
async def buy(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,

        keyboard=[
            [
                types.KeyboardButton(text=payment_command_text())
            ],
            [
                types.KeyboardButton(text=change_model_text()),
                types.KeyboardButton(text=change_system_message_text())
            ]
        ],
        input_field_placeholder="💬 Задай свой вопрос"
    )

    await message.answer(
        text=hello_text,
        reply_markup=keyboard
    )
