import re

from aiogram import types, Router
from aiogram.filters import CommandStart, Command

from bot.agreement.router import agreement_handler
from bot.gpt.command_types import change_model_text, change_system_message_text, balance_text, clear_text
from bot.images import images_command_text
from bot.payment.command_types import balance_payment_command_text
from bot.referral import referral_command_text

startRouter = Router()

from services import GPTModels, tokenizeService

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
            [
                types.KeyboardButton(text=referral_command_text()),
            ],
        ],
        input_field_placeholder="💬 Задай свой вопрос"
    )
    args_match = re.search(r'^/start\s(\S+)', message.text)
    args = args_match.group(1) if args_match else None
    user_id = message.from_user.id
    user_token = await tokenizeService.get_user_tokens(user_id, GPTModels.GPT_4o)

    if user_token is None:
        if args:
            await tokenizeService.get_tokens(user_id, GPTModels.GPT_4o)
            await tokenizeService.get_tokens(user_id, GPTModels.GPT_3_5)
            await tokenizeService.update_user_token(user_id, GPTModels.GPT_4o, 5000)
            await message.answer(text="""
🎉 Вы получили `5 000` токенов!

/balance - ✨ Узнать баланс
""")
            await tokenizeService.update_user_token(args, GPTModels.GPT_4o, 15000)
            await message.bot.send_message(chat_id=args, text="""
🎉 Добавлен новый реферал! Вы получили `15 000` токенов!

/balance - ✨ Узнать баланс
""")
    await message.answer(text=hello_text, reply_markup=keyboard)
    await agreement_handler(message)


@startRouter.message(Command("help"))
async def help_command(message: types.Message):
    await message.bot.send_message(message.chat.id, text="""
Основной ресурc для доступа нейросети - Токены.    
Количество затраченных токенов зависит от длины диалога, ответов нейросети и ваших вопросов.
Для экономии используйте команду - /clear, чтобы не засорять диалог!
Распознование изображений тратит много токенов, будьте внимательны!

/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.
/model - 🤖 Сменить модель, перезапускает бот, позволяет сменить модель бота.
/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить взаимодействие с ботом.   
/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.  
/balance - ✨ Баланс, позволяет узнать оставшиеся количество токенов.
/image - 🖼️ Сгенерировать картинку, вызывает нейросеть Stable Diffusion для генерации изображений.
/buy - 💎 Пополнить баланс, позволяет пополнить баланс токенов.
/referral - ✉️ Получить реферальную ссылку
""")
