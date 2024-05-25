import asyncio
import logging
from tempfile import NamedTemporaryFile

import aiofiles
from aiogram import Router
from aiogram.types import Message, CallbackQuery

from bot.filters import TextCommand, Document, Photo
from bot.gpt import change_model_command
from bot.gpt.command_types import change_system_message_command, change_system_message_text, change_model_text
from bot.gpt.system_messages import get_system_message, system_messages_list, \
    create_system_message_keyboard
from bot.gpt.utils import is_chat_member, send_message, get_response_text, \
    create_change_model_keyboard, checked_text
from bot.utils import include
from services import gptService, GPTModels, completionsService
from services.gpt_service import SystemMessages

gptRouter = Router()


async def handle_gpt_request(message: Message, text: str):
    user_id = message.from_user.id

    try:
        is_subscribe = await is_chat_member(message)

        if not is_subscribe:
            return

        chat_id = message.chat.id

        is_requesting = gptService.get_is_requesting(user_id)

        if is_requesting:
            logging.log(logging.INFO, is_requesting)
            return

        gptService.set_is_requesting(user_id, True)

        message_loading = await message.answer("**⌛️Ожидайте ответ...**")

        await message.bot.send_chat_action(chat_id, "typing")

        system_message = gptService.get_current_system_message(user_id)

        print(get_system_message(system_message))

        answer = completionsService.query_chatgpt(user_id, text, get_system_message(system_message))

        gptService.set_is_requesting(user_id, False)

        await send_message(message, get_response_text(answer))
        await asyncio.sleep(0.5)
        await message_loading.delete()
    except Exception as e:
        logging.log(logging.INFO, e)
        gptService.set_is_requesting(user_id, False)


@gptRouter.message(Photo())
async def handle_document(message: Message):
    await message.answer(
        """
        😔 К сожалению, фотографии пока не поддерживаются!

Следите за обновлениями в канале @gptDeep
        """)


@gptRouter.message(Document())
async def handle_document(message: Message):
    try:
        user_document = message.document if message.document else None
        if user_document:
            with NamedTemporaryFile(delete=False) as temp_file:
                await message.bot.download(user_document, temp_file.name)
            async with aiofiles.open(temp_file.name, 'r', encoding='utf-8') as file:
                await handle_gpt_request(message, await file.read())
    except UnicodeDecodeError as e:
        logging.log(logging.INFO, e)
        await message.answer(
            """
            😔 К сожалению, данный тип файлов не поддерживается!
            
Следите за обновлениями в канале @gptDeep
            """)
    except Exception as e:
        logging.log(logging.INFO, e)


@gptRouter.message(TextCommand([change_system_message_command(), change_system_message_text()]))
async def handle_change_model(message: Message):
    is_subscribe = await is_chat_member(message)

    if not is_subscribe:
        return

    user_id = message.from_user.id

    current_system_message = gptService.get_current_system_message(user_id)

    if not include(system_messages_list, current_system_message):
        current_system_message = SystemMessages.Default.value
        gptService.set_current_system_message(user_id, current_system_message)

    await message.answer(
        text="Установи режим работы бота: ⚙️",
        reply_markup=create_system_message_keyboard(current_system_message)
    )

    await asyncio.sleep(0.5)
    await message.delete()


@gptRouter.message(TextCommand([change_model_command(), change_model_text()]))
async def handle_change_model(message: Message):
    is_subscribe = await is_chat_member(message)

    if not is_subscribe:
        return

    current_model = gptService.get_current_model(message.from_user.id)

    await message.answer(text="Выбери модель: 🤖", reply_markup=create_change_model_keyboard(current_model))
    await asyncio.sleep(0.5)
    await message.delete()


async def handle_change_system_message(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    system_message = callback_query.data
    current_system_message = gptService.get_current_system_message(user_id)

    if system_message == current_system_message:
        await callback_query.answer(f"Данный режим уже выбран!")
        return

    gptService.set_current_system_message(user_id, system_message)

    await callback_query.message.edit_reply_markup(
        reply_markup=create_system_message_keyboard(system_message)
    )

    await asyncio.sleep(0.5)

    await callback_query.answer(f"Режим успешно изменён!")
    await callback_query.message.delete()


async def handle_change_model(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    gpt_model = GPTModels(callback_query.data)
    current_gpt_model = gptService.get_current_model(user_id)

    if gpt_model.value == current_gpt_model.value:
        await callback_query.answer(f"Модель {current_gpt_model.value} уже выбрана!")
        return

    gptService.set_current_model(user_id, gpt_model)

    await callback_query.message.edit_reply_markup(
        reply_markup=create_change_model_keyboard(gpt_model)
    )

    await asyncio.sleep(0.5)

    await callback_query.answer(f"Текущая модель успешно сменена на {checked_text(gpt_model.value)}")
    await callback_query.message.delete()


@gptRouter.callback_query()
async def handle_change_model_query(callback_query: CallbackQuery):
    if include(system_messages_list, callback_query.data):
        await handle_change_system_message(callback_query)
    if callback_query.data.startswith('gpt'):
        await handle_change_model(callback_query)


@gptRouter.message()
async def handle_completion(message: Message):
    await handle_gpt_request(message, message.text)
