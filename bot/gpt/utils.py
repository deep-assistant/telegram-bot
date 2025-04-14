import logging

from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.main_keyboard import send_message
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

    check_result = chat_member.status in ['member', 'administrator', 'creator']

    print(f"User {user_id} is subscribed as: {check_result}")

    return check_result


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


def get_tokens_message(tokens_spent: int, tokens_left: int, requested_model: str = None, responded_model: str = None):
    if tokens_spent <= 0:
        return None
    
    if responded_model and (requested_model == responded_model):
        return f"""🤖 Ответ от: *{responded_model}*

✨ Затрачено: *{tokens_spent}⚡️* (осталось *{tokens_left}⚡️*)"""
    elif requested_model and responded_model:
        return f"""🤖 Ответ от: *{responded_model}*
⚠️ Выбранная модель *{requested_model}* временно недоступна!

✨ Затрачено: *{tokens_spent}⚡️* (осталось *{tokens_left}⚡️*)"""
    elif requested_model:
        return f"""🤖 Ответ от: *{requested_model}* (но это *не точно*)
⚠️ Если вы видите это сообщение, напишите об этом в разделе *Ошибки* в нашем собществе @deepGPT.

✨ Затрачено: *{tokens_spent}⚡️* (осталось *{tokens_left}⚡️*)"""
    else:
        return f"""🤖 Ответ от: *неизвестно* (не удалось определить модель)
⚠️ Если вы видите это сообщение, напишите об этом в разделе *Ошибки* в нашем собществе @deepGPT.

✨ Затрачено: *{tokens_spent}⚡️* (осталось *{tokens_left}⚡️*)"""

def quote_message(text):
    return '> ' + text.replace('\n', '\n> ')

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

async def send_markdown_message(message: Message, text: str):
    parts = split_message(text)
    for part in parts:
        try:
            await send_message(message, text=telegramify_markdown.markdownify(part), parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            await send_message(message, text=part, parse_mode=None)
            logging.error(f"Failed to send message as markdown: {e}")
    return parts

def create_change_model_keyboard(current_model: GPTModels):
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.O3_mini, current_model),
                callback_data=GPTModels.O3_mini.value
            )
        ],
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
                text=get_model_text(GPTModels.DeepSeek_Chat, current_model),
                callback_data=GPTModels.DeepSeek_Chat.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.DeepSeek_Reasoner, current_model),
                callback_data=GPTModels.DeepSeek_Reasoner.value
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Claude_3_5_Sonnet, current_model),
                callback_data=GPTModels.Claude_3_5_Sonnet.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Claude_3_7_Sonnet, current_model),
                callback_data=GPTModels.Claude_3_7_Sonnet.value
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Claude_3_Opus, current_model),
                callback_data=GPTModels.Claude_3_Opus.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Claude_3_5_Haiku, current_model),
                callback_data=GPTModels.Claude_3_5_Haiku.value
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_Auto, current_model),
                callback_data=GPTModels.GPT_Auto.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.GPT_4_Unofficial, current_model),
                callback_data=GPTModels.GPT_4_Unofficial.value
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
        [
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Llama3_1_70B, current_model),
                callback_data=GPTModels.Llama3_1_70B.value
            ),
            InlineKeyboardButton(
                text=get_model_text(GPTModels.Llama3_1_8B, current_model),
                callback_data=GPTModels.Llama3_1_8B.value
            ),
        ]
    ])
