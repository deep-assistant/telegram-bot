import asyncio

from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot.api.command_types import api_command
from bot.filters import TextCommand, TextCommandQuery
from services import tokenizeService

apiRouter = Router()


def get_api_message(token):
    return {
        "text": f"""API KEY: `{token['id']}` \n"""
                f"""API URL: https://api.deep-foundation.tech/v1/ \n"""
                f"""API URL Whisper: https://api.deep-foundation.tech/v1/audio/transcriptions  \n"""
                f"""API URL Completions: https://api.deep-foundation.tech/v1/chat/completions \n\n"""
                f"""Ваш баланс: {token['tokens_gpt']}⚡️️ \n\n"""
                f"""https://github.com/deep-foundation/deep-gpt/blob/main/docs.md - 📄 Документация по работе с API""",
        "reply_markup": InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[[InlineKeyboardButton(text="Перегенерировать токен 🔄", callback_data="regenerate_token")]]
        )
    }


@apiRouter.message(TextCommand([api_command()]))
async def handle_api_message(message: Message):
    token = await tokenizeService.get_api_token(message.from_user.id)

    await message.answer(**get_api_message(token))


@apiRouter.callback_query(TextCommandQuery(["regenerate_token"]))
async def handle_change_system_message_query(callback_query: CallbackQuery):
    token = await tokenizeService.regenerate_api_token(callback_query.from_user.id)
    await asyncio.sleep(1)
    await callback_query.message.edit_text(**get_api_message(token))
    await callback_query.answer("✅ Токен успешно обновлен!")
