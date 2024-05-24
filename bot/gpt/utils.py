from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import IS_DEV
from services.gpt_service import GPTModels


def checked_model_text(model: GPTModels):
    return f"{model.value} ✅"


def get_model_text(model: GPTModels, current_model: GPTModels):
    if model.value == current_model.value:
        return checked_model_text(model)

    return model.value


subscribe_text = """
📰 Чтобы пользоваться ботом необходимо подписаться на наш канал! @gptDeep

Следите за обновлениями и новостями у нас в канале!
"""


async def check_subscription(message: Message) -> bool:
    if IS_DEV:
        return True

    chat_member = await message.bot.get_chat_member(chat_id=-1002239712203, user_id=message.from_user.id)

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


def get_response_text(answer):
    remaining_user_tokens = answer.get("remainingTokens").get('remainingUserTokens')
    remaining_chat_gpt_tokens = answer.get("remainingTokens").get('remainingChatGptTokens')
    request_tokens_used = answer.get("tokensUsed").get('requestTokensUsed')
    response_tokens_used = answer.get("tokensUsed").get('responseTokensUsed')

    if answer.get("success"):
        return f"""{answer.get('response')}
            
🥰 Затрачено `{request_tokens_used}` | Осталось `{remaining_user_tokens}` **юзер** токенов
🤖 Затрачено `{response_tokens_used}` | Осталось `{remaining_chat_gpt_tokens}` **нейросетевых** токенов
            """

    return answer.get("response")
