import asyncio
import logging
import re

from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery

from bot.filters import StartWithQuery
from bot.gpt.command_types import change_model_text, change_system_message_text, balance_text, clear_text
from bot.gpt.utils import check_subscription
from bot.images import images_command_text
from bot.payment.command_types import balance_payment_command_text
from bot.referral import referral_command_text
from services import GPTModels, tokenizeService

startRouter = Router()

hello_text = """
👋 Привет! Я бот от deep.foundation!

В боте есть бесплатная модель gpt-3.5-turbo, каждый день на ее счет начисляется 50,000 токенов!

🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение! 

Приводи друзей и получай еще больше бесплатных запросов!
/referral - получить свою реферальную ссылку.

/help - Обзор все команд бота.
/balance - ✨ Узнать свой баланс
"""

ref_text = """
👋 Ты прибыл по реферальной ссылке, чтобы получить награду ты должен подписаться на наш канал. 👊🏻
"""


async def create_token_if_not_exist(user_id):
    user_token = await tokenizeService.get_user_tokens(user_id, GPTModels.GPT_4o)
    if user_token is None:
        await tokenizeService.get_tokens(user_id, GPTModels.GPT_4o)
        await tokenizeService.get_tokens(user_id, GPTModels.GPT_3_5)
        await tokenizeService.update_user_token(user_id, GPTModels.GPT_4o, 15000 - 1500)
        await tokenizeService.check_tokens_update_tokens(user_id)

    return user_token


async def apply_ref(message: types.Message, user_id, ref_user_id: str):
    user_token = await tokenizeService.get_user_tokens(user_id, GPTModels.GPT_4o)

    if user_token is None and str(ref_user_id) != str(user_id):
        if ref_user_id:
            logging.log(logging.INFO, f"Новый реферал {ref_user_id} -> {user_id}!")

        await create_token_if_not_exist(user_id)
        await tokenizeService.update_user_token(user_id, GPTModels.GPT_3_5, 5000)
        await tokenizeService.update_user_token(user_id, GPTModels.GPT_4o, 5000)
        await message.answer(text="""
🎉 Вы получили `5 000` токенов!

/balance - ✨ Узнать баланс
""")

        await create_token_if_not_exist(ref_user_id)

        await tokenizeService.update_user_token(ref_user_id, GPTModels.GPT_4o, 15000)
        await message.bot.send_message(chat_id=ref_user_id, text="""
🎉 Добавлен новый реферал! Вы получили `15 000` токенов!

/balance - ✨ Узнать баланс
""")


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
    ref_user_id = args_match.group(1) if args_match else None
    print(ref_user_id)

    await message.answer(text=hello_text, reply_markup=keyboard)

    is_subscribe = await check_subscription(message)

    if ref_user_id is None:
        await create_token_if_not_exist(message.from_user.id)

    if not is_subscribe:
        if str(ref_user_id) == str(message.from_user.id):
            return

        await message.answer(
            text=ref_text,
            reply_markup=types.InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="Подписаться 👊🏻", url="https://t.me/gptDeep"),
                    ],
                    [
                        types.InlineKeyboardButton(text="Проверить ✅",
                                                   callback_data=f"ref-is-subscribe {ref_user_id} {message.from_user.id}"),
                    ]
                ]
            )
        )

        return

    if ref_user_id is None:
        return
    print(ref_user_id, '129')
    await apply_ref(message, message.from_user.id, ref_user_id)


@startRouter.callback_query(StartWithQuery("ref-is-subscribe"))
async def handle_ref_is_subscribe_query(callback_query: CallbackQuery):
    ref_user_id = callback_query.data.split(" ")[1]
    user_id = callback_query.data.split(" ")[2]

    is_subscribe = await check_subscription(callback_query.message, user_id)

    if not is_subscribe:
        await callback_query.message.answer(text="Вы не подписались! 😡")
        return

    await apply_ref(callback_query.message, user_id, ref_user_id)


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
