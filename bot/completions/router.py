from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message

from services import completionsService

completionsRouter = Router()


@completionsRouter.message()
async def handle_callback_query(message: Message):
    await message.bot.send_chat_action(message.chat.id, "typing")

    await message.answer(
        completionsService.query_chatgpt(
            message.from_user.id,
            message.text
        ),
        parse_mode=ParseMode.MARKDOWN
    )
