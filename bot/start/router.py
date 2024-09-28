import re

from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.filters import StartWithQuery
from bot.filters import TextCommand
from bot.gpt.command_types import change_model_text, change_system_message_text, balance_text, clear_text, \
    get_history_text, help_text, help_command, app_command
from bot.gpt.utils import check_subscription
from bot.images import images_command_text
from bot.payment.command_types import balance_payment_command_text
from bot.referral import referral_command_text
from services import tokenizeService, referralsService

startRouter = Router()

hello_text = """
👋 Привет! Я бот от deep.foundation!

Бот бесплатный, каждый день тебе будет начисляться базовый баланс от *10,000*⚡️ (энергия)!

/referral - Увеличивай свои награды с реферальной системой!
15 000⚡️️ за каждого приглашенного пользователя. 
+500⚡️️ к ежедневному пополнению баланса за каждого пользователя. 

Приводи друзей и получай еще больше бесплатных ⚡️!

🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение! 

Так же, у нас есть очень удобное приложение, встроенное прямо в телеграм!
https://t.me/DeepGPTBot/DeepGPT

/help - Обзор все команд бота.
/balance - ✨ Узнать свой баланс
/referral - 🔗 Подробности рефералки
"""

ref_text = """
👋 Ты прибыл по реферальной ссылке, чтобы получить награду ты должен подписаться на наш канал. 👊🏻
"""


async def handle_referral(message, user_id, ref_user_id):
    result = await referralsService.create_referral(user_id, ref_user_id)

    if result["parent"] is not None:
        await message.answer(text="""
🎉 Вы получили *5 000*⚡️!

/balance - ✨ Узнать баланс
/referral - 🔗 Подробности рефералки
""")

        await message.bot.send_message(chat_id=ref_user_id, text="""
🎉 Добавлен новый реферал! 
Вы получили *5 000*⚡️!
Ваш реферал должен проявить любую активность в боте через 24 часа, чтобы вы получили еще *5 000*⚡️ и +500⚡️️ к ежедневному пополнению баланса.

/balance - ✨ Узнать баланс
/referral - 🔗 Подробности рефералки
""")


async def create_token_if_not_exist(user_id):
    return await tokenizeService.get_tokens(user_id)


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
                types.KeyboardButton(text=help_text()),
                types.KeyboardButton(text=get_history_text())
            ],
            [
                types.KeyboardButton(text=referral_command_text()),
            ],
        ],
        input_field_placeholder="💬 Задай свой вопрос"
    )
    args_match = re.search(r'^/start\s(\S+)', message.text)
    ref_user_id = args_match.group(1) if args_match else None

    await message.answer(text=hello_text, reply_markup=keyboard)

    is_subscribe = await check_subscription(message)

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

    await handle_referral(message, message.from_user.id, ref_user_id)


@startRouter.callback_query(StartWithQuery("ref-is-subscribe"))
async def handle_ref_is_subscribe_query(callback_query: CallbackQuery):
    ref_user_id = callback_query.data.split(" ")[1]
    user_id = callback_query.data.split(" ")[2]

    is_subscribe = await check_subscription(callback_query.message, user_id)

    if not is_subscribe:
        await callback_query.message.answer(text="Вы не подписались! 😡")
        return

    await handle_referral(callback_query.message, user_id, ref_user_id)


@startRouter.message(TextCommand([help_command(), help_text()]))
async def help_command(message: types.Message):
    await message.answer(text="""
Основной ресурc для доступа нейросети - ⚡️ (энергия).
Это универсальный ресурс для всего функционала нейросети.

Каждый функционал тратит разное количество ⚡️.
Количество затраченных ⚡️ зависит от длины диалога, ответов нейросети и ваших вопросов.
Для экономии используйте команду - /clear, чтобы не засорять диалог!

/app - 🔥 Получить ссылку к приложению!
/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.
/model - 🤖 Сменить модель, перезапускает бот, позволяет сменить модель бота.
/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить взаимодействие с ботом.   
/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.  
/balance - ✨ Баланс, позволяет узнать баланс ⚡️.
/image - 🖼️ Сгенерировать картинку, вызывает нейросеть Stable Diffusion для генерации изображений.
/buy - 💎 Пополнить баланс, позволяет пополнить баланс ⚡️.
/referral - 🔗 Получить реферальную ссылку
/suno - 🎵 Генерация песен через suno
/text - Отправить текстовое сообщение
""")


@startRouter.message(TextCommand([app_command()]))
async def app_handler(message: Message):
    await message.answer("""Ссылка на приложение: https://t.me/DeepGPTBot/DeepGPT""")
