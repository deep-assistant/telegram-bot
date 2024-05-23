from aiogram import Router
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot.filters import TextCommand
from bot.gpt import change_model_command
from services import completionsService
from services.gpt_service import gptService, GPTModels

gptRouter = Router()


def checked_model_text(model: GPTModels):
    return f"{model.value} ✅"


def get_model_text(model: GPTModels, current_model: GPTModels):
    if model.value == current_model.value:
        return checked_model_text(model)

    return model.value


async def is_chat_member(message: Message) -> bool:
    chat_member = await message.bot.get_chat_member(chat_id=-1002239712203, user_id=message.chat.id)

    is_subscribe = check_subscription(chat_member.status)

    if not is_subscribe:
        await message.answer(
            text=subscribe_text,
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[[InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/gptDeep")]]
            )
        )

    return is_subscribe


@gptRouter.message(TextCommand(change_model_command()))
async def handle_change_model(message: Message):
    is_subscribe = await is_chat_member(message)

    if not is_subscribe:
        return

    current_model = gptService.get_current_model(message.from_user.id)

    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_4o, current_model),
                callback_data=GPTModels.GPT_4o.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_3_5, current_model),
                callback_data=GPTModels.GPT_3_5.value
            )
        ]
    ])

    await message.answer(text="Выбери модель: 🤖", reply_markup=keyboard)
    await message.delete()


@gptRouter.callback_query()
async def handle_change_model_query(callback_query: CallbackQuery):
    print(callback_query.data)
    if not callback_query.data.startswith('gpt'):
        return

    user_id = callback_query.from_user.id

    gpt_model = GPTModels(callback_query.data)
    current_gpt_model = gptService.get_current_model(user_id)

    if gpt_model.value == current_gpt_model.value:
        await callback_query.answer(f"Модель {current_gpt_model.value} уже выбрана!")
        return

    gptService.set_current_model(user_id, gpt_model)

    await callback_query.answer(f"Текущая модель успешно сменена на {checked_model_text(gpt_model)}")
    await callback_query.message.delete()


def check_subscription(status: ChatMemberStatus) -> bool:
    return status in ['member', 'administrator', 'creator']


subscribe_text = """
📰 Чтобы пользоваться ботом необходимо подписаться на наш канал! @gptDeep

Следите за обновлениями и новостями у нас в канале!
"""


@gptRouter.message()
async def handle_completion(message: Message):
    is_subscribe = await is_chat_member(message)

    if not is_subscribe:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    is_requesting = gptService.get_is_requesting(user_id)

    if is_requesting:
        print(is_requesting)
        return

    gptService.set_is_requesting(user_id, True)

    message_loading = await message.answer("**⌛️Ожидайте ответ...**")

    answer = completionsService.query_chatgpt(
        message.from_user.id,
        message.text
    )

    await message.bot.edit_message_text(answer, chat_id, message_loading.message_id)

    gptService.set_is_requesting(user_id, False)
