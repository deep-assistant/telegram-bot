import logging

from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from services.gpt_service import GPTModels
import telegramify_markdown

def checked_text(value: str):
    return f"✅ {value}"


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
🤖 Затрачено на запрос *{tokens}* `energy` ⚡

❔ /help - Информация по `energy` ⚡
"""


def split_message(message):
    max_symbols = 3990
    messages = []
    current_message = ''
    current_language = ''
    in_code_block = False
    lines = message.split('\n')

    for line in lines:
        is_code_block_line = line.startswith('```')
        if is_code_block_line:
            current_language = line[3:].strip()
            in_code_block = not in_code_block

        potential_message = (current_message + '\n' if current_message else '') + line

        if len(potential_message) > max_symbols:
            if in_code_block:
                current_message += '\n```'

            messages.append(current_message)

            if in_code_block:
                current_message = f'```{current_language}\n{line}'
            else:
                current_message = line
        else:
            current_message = potential_message

    if current_message:
        if in_code_block:
            current_message += '\n```'
        messages.append(current_message)

    return messages


async def send_message(message: Message, text: str):
    parts = split_message(text)

    for part in parts:
        try:
            await message.answer(telegramify_markdown.markdownify(part), parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            logging.log(logging.INFO, e)
            await message.answer(part, parse_mode=None)

    return parts

def create_change_model_keyboard(current_model: GPTModels):
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.O1_preview, current_model),
                callback_data=GPTModels.O1_preview.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.O1_mini, current_model),
                callback_data=GPTModels.O1_mini.value
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Claude_3_5_Sonnet, current_model),
                callback_data=GPTModels.Claude_3_5_Sonnet.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Claude_3_Opus, current_model),
                callback_data=GPTModels.Claude_3_Opus.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Claude_3_Haiku, current_model),
                callback_data=GPTModels.Claude_3_Haiku.value
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_4o, current_model),
                callback_data=GPTModels.GPT_4o.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_4o_mini, current_model),
                callback_data=GPTModels.GPT_4o_mini.value
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_3_5, current_model),
                callback_data=GPTModels.GPT_3_5.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Llama3_1_405B, current_model),
                callback_data=GPTModels.Llama3_1_405B.value
            )
        ],
        # [
        #     InlineKeyboardButton(
        #         text=get_model_text(GPTModels.Uncensored, current_model),
        #         callback_data=GPTModels.Uncensored.value
        #     ),
        # ],
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Llama3_1_70B, current_model),
                callback_data=GPTModels.Llama3_1_70B.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Llama3_1_8B, current_model),
                callback_data=GPTModels.Llama3_1_8B.value
            ),
        ],

    ])
