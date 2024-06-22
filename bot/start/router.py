from aiogram import types, Router
from aiogram.filters import CommandStart, Command

from bot.agreement.router import agreement_handler
from bot.gpt.command_types import change_model_text, change_system_message_text, balance_text, clear_text
from bot.images import images_command_text
from bot.payment.command_types import balance_payment_command_text

startRouter = Router()

hello_text = """
👋 Привет! Я самый умный бот, я использую в себе самые мощные нейросети на данный момент!

🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение! 

/help - Обзор все команд бота.
"""


@startRouter.message(CommandStart())
async def buy(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                types.KeyboardButton(text=balance_text()),
                types.KeyboardButton(text=balance_payment_command_text())
            ],
            [
                types.KeyboardButton(text=change_model_text()),
                types.KeyboardButton(text=change_system_message_text())
            ],
            [
                types.KeyboardButton(text=clear_text()),
                types.KeyboardButton(text=images_command_text())
            ],
        ],
        input_field_placeholder="💬 Задай свой вопрос"
    )

    await message.answer(text=hello_text, reply_markup=keyboard)
    await agreement_handler(message)


@startRouter.message(Command("help"))
async def help_command(message: types.Message):
    await message.bot.send_message(message.chat.id, text="""
/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.
/model - 🤖 Сменить модель, перезапускает бот, позволяет сменить модель бота.
/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить взаимодействие с ботом.   
/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.  
/balance - ✨ Баланс, позволяет узнать оставшиеся количество токенов.
/image - 🖼️ Сгенерировать картинку, вызывает нейросеть Stable Diffusion для генерации изображений.
/buy - 💎 Пополнить баланс, позволяет пополнить баланс токенов.
""")
