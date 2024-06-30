import logging

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from services import tokenizeService
from services.gpt_service import GPTModels


def checked_text(value: str):
    return f"{value} ✅"


def get_model_text(model: GPTModels, current_model: GPTModels):
    if model.value == current_model.value:
        return checked_text(model.value)

    return model.value


subscribe_text = """
📰 Чтобы пользоваться ботом необходимо подписаться на наш канал! @gptDeep

Следите за обновлениями и новостями у нас в канале!
"""


async def check_subscription(message: Message, id: str = None) -> bool:
    user_id = id if id is not None else message.from_user.id

    chat_member = await message.bot.get_chat_member(chat_id=-1002239712203, user_id=user_id)

    return chat_member.status in ['member', 'administrator', 'creator']


async def is_chat_member(message: Message) -> bool:
    await tokenizeService.check_tokens_update_tokens(message.from_user.id)
    is_subscribe = await check_subscription(message)

    if not is_subscribe:
        await message.answer(
            text=subscribe_text,
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[[InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/gptDeep")]]
            )
        )

    return is_subscribe


def get_tokens_message(tokens: int):
    if tokens <= 0:
        return None

    return f"""
🤖 Затрачено на запрос  `{tokens}` токенов.
❔ /help - Информация по токенам
"""


def split_string_by_length(string: str, length=4096):
    return [string[i:i + length] for i in range(0, len(string), length)]


async def send_message(message: Message, text: str):
    parts = split_string_by_length(text)

    for part in parts:
        try:
            await message.answer(part)
        except Exception as e:
            logging.log(logging.INFO, e)
            await message.answer(part, parse_mode=None)


def create_change_model_keyboard(current_model: GPTModels):
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_4o, current_model),
                callback_data=GPTModels.GPT_4o.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_3_5, current_model),
                callback_data=GPTModels.GPT_3_5.value
            ),
            # InlineKeyboardButton(
            #     text=get_model_text(GPTModels.Llama3_8b, current_model),
            #     callback_data=GPTModels.Llama3_8b.value
            # )
        ]
    ])
