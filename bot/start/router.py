import re

from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.filters import StartWithQuery
from bot.filters import TextCommand
from bot.commands import help_text, help_command, app_command
from bot.gpt.utils import check_subscription
from bot.main_keyboard import create_main_keyboard, send_message
from services import tokenizeService, referralsService

startRouter = Router()

hello_text = """
👋 Привет! Я бот от разработчиков deep.foundation!

🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение или нажми кнопку в меню!

/help - ✨ обзор команд и возможностей
/balance - ⚡️ узнать свой баланс
/referral - 🔗 подробности рефералки

Всё бесплатно, если не платить.
Каждый день твой баланс будет пополняться на сумму от *10 000⚡️* (энергии)!

Если нужно больше:
💎 Можно пополнить баланс Telegram звёздами или банковской картой.
👥 Понравилось? Поделись с друзьями и получи бонус за каждого приглашенного друга! Приводя много друзей ты сможешь пользоваться нейросетями практически безлимитно.

/referral - получай больше с реферальной системой:
*5 000⚡️️* за каждого приглашенного пользователя;
*+500⚡️️* к ежедневному пополнению баланса за каждого друга.

🏠 Если что-то пошло не так или хочешь поделиться вдохновением, напиши в наше сообщество @deepGPT.
"""

ref_text = """
👋 Ты прибыл по реферальной ссылке, чтобы получить награду нужно подписаться на мой канал.
"""

async def handle_referral(message, user_id, ref_user_id):
    result = await referralsService.create_referral(user_id, ref_user_id)
    
    print(result, 'resuuuuult')
    
    # Проверяем, что ref_user_id валиден перед отправкой сообщения
    if not ref_user_id:
        return  # Прерываем выполнение, если ref_user_id отсутствует
    
    if not result or result.get("parent") is None:
        return
    
    # Проверяем, что ref_user_id - число или строка (например, username)
    try:
        chat_id = int(ref_user_id)  # Если ref_user_id должен быть числом
    except (TypeError, ValueError):
        await message.answer("❌ Некорректный реферальный ID.")
        return
    
    await message.answer(text="""
🎉 Вы получили *5 000*⚡️!

/balance - ✨ Узнать баланс
/referral - 🔗 Подробности рефералки
""")

    await message.bot.send_message(
        chat_id=chat_id,  # Используем проверенный chat_id
        text="""
🎉 Добавлен новый реферал! 
Вы получили *5 000*⚡️!
Вы получите *5 000*⚡️ и +500⚡️️ к ежедневному пополнению баланса, если ваш реферал подпишется на канал @gptDeep и проявит активность в боте.

/balance - ✨ Узнать баланс
/referral - 🔗 Подробности рефералки
"""
    )


async def create_token_if_not_exist(user_id):
    return await tokenizeService.get_tokens(user_id)

@startRouter.message(CommandStart())
async def start(message: types.Message):
    args_match = re.search(r'^/start\s(\S+)', message.text)
    ref_user_id = args_match.group(1) if args_match else None

    # always force sending the keyboard
    keyboard = create_main_keyboard()
    await send_message(message, text=hello_text, reply_markup=keyboard)

    await create_token_if_not_exist(message.from_user.id)

    is_subscribe = await check_subscription(message)

    # Уведомляем реферера, что пользователь перешёл по ссылке, но ещё не подписался
    if ref_user_id: # and str(ref_user_id) != str(message.from_user.id) and not is_subscribe
        try:
            chat_id = int(ref_user_id)
        except (TypeError, ValueError):
            chat_id = None

        if chat_id:
            user_name = message.from_user.username
            user_mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
            await message.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"""
🎉 По вашей реферальной ссылке перешли: @{user_name} ({user_mention}).

Чтобы вашему другу стать вашим рефералом, он должен подписаться на канал @gptDeep.

Как только это произойдёт вы получите <b>5 000</b>⚡️ единоразово и <b>+500</b>⚡️️ к ежедневному пополнению баланса.

Если вдруг этого долго не происходит, то возможно вашему другу нужна помощь, <b>попробуйте написать ему в личные сообщения</b>. 
Если и это не помогает, то обратитесь в поддержку в сообществе @deepGPT и мы поможем вам разобраться с ситуацией.
"""
                ),
                parse_mode="HTML"
            )

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
Основной ресурc для доступа к нейросетям - ⚡️ (энергия).
Это универсальный ресурс для всего функционала бота.

Каждая нейросеть тратит разное количество ⚡️.
Количество затраченных ⚡️ зависит от длины истории диалога, моделей нейросетей и объёма ваших вопросов и ответов от нейросети.
Для экономии используйте команду - /clear, чтобы не переполнять историю диалога и не увеличивать расход ⚡️ (энергии)! 
Рекомендуется очищать контекст перед началом обсуждения новой темы. А также если выбранная модель начала отказывать в помощи.

/app - 🔥 Получить ссылку к приложению!
/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.
/model - 🛠️ Сменить модель, перезапускает бот, позволяет сменить модель бота.
/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить режим взаимодействия с ботом.   
/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.  
/balance - ✨ Баланс, позволяет узнать баланс ⚡️.
/image - 🖼️ Генерация картинки (Midjourney, DALL·E 3, Flux, Stable Diffusion)
/buy - 💎 Пополнить баланс, позволяет пополнить баланс ⚡️.
/referral - 🔗 Получить реферальную ссылку
/suno - 🎵 Генерация музыки (Suno)
/text - Отправить текстовое сообщение
""")


@startRouter.message(TextCommand([app_command()]))
async def app_handler(message: Message):
    await message.answer("""Ссылка на приложение: https://t.me/DeepGPTBot/App""")
