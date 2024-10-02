import asyncio
import io
import json
import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

import aiofiles
from aiogram import Router
from aiogram import types
from aiogram.types import BufferedInputFile, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, CallbackQuery

from bot.agreement import agreement_handler
from bot.filters import TextCommand, Document, Photo, TextCommandQuery, Voice, StateCommand, StartWithQuery, Video
from bot.gpt import change_model_command
from bot.gpt.command_types import change_system_message_command, change_system_message_text, change_model_text, \
    balance_text, balance_command, clear_command, clear_text, get_history_command, get_history_text
from bot.gpt.system_messages import get_system_message, system_messages_list, \
    create_system_message_keyboard
from bot.gpt.utils import is_chat_member, send_message, get_tokens_message, \
    create_change_model_keyboard, checked_text
from bot.middlewares.MiddlewareAward import MiddlewareAward
from bot.utils import include
from bot.utils import send_photo_as_file
from config import TOKEN, GO_API_KEY
from services import gptService, GPTModels, completionsService, tokenizeService, referralsService, stateService, \
    StateTypes, systemMessage
from services.gpt_service import SystemMessages
from services.image_utils import format_image_from_request
from services.utils import async_post, async_get

gptRouter = Router()

questionAnswer = False

gptRouter.message.middleware(MiddlewareAward())


async def answer_markdown_file(message: Message, md_content: str):
    file_path = f"markdown_files/{uuid.uuid4()}.md"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    await message.answer_document(FSInputFile(file_path), caption="Сообщение в формате markdown")

    os.remove(file_path)


async def handle_gpt_request(message: Message, text: str):
    user_id = message.from_user.id
    message_loading = await message.answer("**⌛️Ожидайте ответ...**")

    try:
        is_agreement = await agreement_handler(message)

        if not is_agreement:
            return

        is_subscribe = await is_chat_member(message)

        if not is_subscribe:
            return

        chat_id = message.chat.id

        bot_model = gptService.get_current_model(user_id)
        gpt_model = gptService.get_mapping_gpt_model(user_id)

        await message.bot.send_chat_action(chat_id, "typing")

        system_message = gptService.get_current_system_message(user_id)

        gpt_tokens_before = await tokenizeService.get_tokens(user_id)

        if gpt_tokens_before.get("tokens", 0) <= 0:
            await message.answer(
                text=f"""
Ошибка 😔: Превышен лимит использования!

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс 
/referral - Пригласить друга, чтобы получить бесплатно `energy` ⚡!
/model - Сменить модель
""")
            return
        system_message = get_system_message(system_message)
        if system_message == "question-answer":
            questionAnswer = True
        else:
            questionAnswer = False

        answer = await completionsService.query_chatgpt(
            user_id,
            text,
            system_message,
            gpt_model,
            bot_model,
            questionAnswer,
        )

        if not answer.get("success"):
            if answer.get('response') == "Ошибка 😔: Превышен лимит использования токенов.":
                await message.answer(
                    text=f"""
{answer.get('response')}

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс 
/referral - Пригласить друга, чтобы получить бесплатно `energy`⚡!
/model - Сменить модель
""",
                )
                await asyncio.sleep(0.5)
                await message_loading.delete()

                return

            await message.answer(answer.get('response'))
            await asyncio.sleep(0.5)
            await message_loading.delete()

            return

        gpt_tokens_after = await tokenizeService.get_tokens(user_id)

        format_text = format_image_from_request(answer.get("response"))
        image = format_text["image"]

        messages = await send_message(message, format_text["text"])

        if len(messages) > 1:
            await answer_markdown_file(message, format_text["text"])

        if image is not None:
            await message.answer_photo(image)
            await send_photo_as_file(message, image, "Вот картинка в оригинальном качестве")
        await asyncio.sleep(0.5)
        await message_loading.delete()
        await message.answer(get_tokens_message(gpt_tokens_before.get("tokens", 0) - gpt_tokens_after.get("tokens", 0)))
    except Exception as e:
        logging.log(logging.INFO, e)


async def get_photos_links(message, photos):
    images = []

    for photo in photos:
        file_info = await message.bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        images.append({"type": "image_url", "image_url": {"url": file_url}})

    return images


@gptRouter.message(Video())
async def handle_image(message: Message):
    print(message.video)


@gptRouter.message(Photo())
async def handle_image(message: Message, album):
    photos = []

    for item in album:
        photos.append(item.photo[-1])

    tokens = await tokenizeService.get_tokens(message.from_user.id)

    if tokens.get("tokens") <= 0:
        await message.answer("""
У вас не хватает `energy` ⚡!

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - Пригласить друга, чтобы получить бесплатно `energy`⚡!
""")
        return

    is_subscribe = await is_chat_member(message)

    if not is_subscribe:
        return

    text = "Опиши" if message.caption is None else message.caption

    await message.bot.send_chat_action(message.chat.id, "typing")

    content = await get_photos_links(message, photos)

    content.append({"type": "text", "text": text})

    bot_model = gptService.get_current_model(message.from_user.id)

    if bot_model.value != GPTModels.GPT_4o_mini.value:
        gptService.set_current_model(message.from_user.id, GPTModels.GPT_4o_mini)
        await message.answer("""
Для взаимодействия с картинками модель автоматически была сменена на `GPT-4o-mini`.        

Сменить модель - /models
        """)

    await handle_gpt_request(message, content)


async def transcribe_voice_sync(voice_file_url: str):
    headers = {
        "Authorization": f"Bearer {GO_API_KEY}",
    }

    voice_response = await async_get(voice_file_url)
    if voice_response.status_code == 200:
        voice_data = voice_response.content

        files = {
            'file': ('audio.ogg', voice_data, 'audio/ogg'),
            'model': (None, 'whisper-1')
        }

        post_response = await async_post("https://api.goapi.ai/v1/audio/transcriptions", headers=headers, files=files)
        if post_response.status_code == 200:
            return {"success": True, "text": post_response.json()["text"]}
        else:
            return {"success": False, "text": f"Error: {post_response.status_code}"}
    else:
        return {"success": False, "text": f"Error: {voice_response.status_code}"}


executor = ThreadPoolExecutor()


async def transcribe_voice(voice_file_url: str):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(executor, transcribe_voice_sync, voice_file_url)
    return await response


@gptRouter.message(Voice())
async def handle_voice(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        if message.entities is None:
            return
        mentions = [entity for entity in message.entities if entity.type == 'mention']
        if not any(mention.offset <= 0 < mention.offset + mention.length for mention in mentions):
            return
    tokens = await tokenizeService.get_tokens(message.from_user.id)

    if tokens.get("tokens") <= 0:
        await message.answer("""
У вас не хватает `energy` ⚡ 

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - Пригласить друга, чтобы получить бесплатно `energy` ⚡!  
""")
        return

    is_subscribe = await is_chat_member(message)

    if not is_subscribe:
        return

    duration = message.voice.duration
    voice_file_id = message.voice.file_id
    file = await message.bot.get_file(voice_file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

    response_json = await transcribe_voice(file_url)

    tokens = duration * 30
    if response_json.get("success"):
        await message.answer(f"""
🎤 Обработка аудио затратила `{tokens}` `energy` ⚡ 

❔ /help - Информация по `energy` ⚡
""")
        await tokenizeService.update_user_token(message.from_user.id, tokens, 'subtract')

        await handle_gpt_request(message, response_json.get('text'))
        return

    await message.answer(response_json.get('text'))


@gptRouter.message(Document())
async def handle_document(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        if message.caption_entities is None:
            return
        mentions = [entity for entity in message.caption_entities if entity.type == 'mention']
        if not any(mention.offset <= 0 < mention.offset + mention.length for mention in mentions):
            return
    try:
        user_document = message.document if message.document else None
        if user_document:
            with NamedTemporaryFile(delete=False) as temp_file:
                await message.bot.download(user_document, temp_file.name)
            async with aiofiles.open(temp_file.name, 'r', encoding='utf-8') as file:
                text = await file.read()
                caption = message.caption if message.caption is not None else ""
                await handle_gpt_request(message, f"{caption}\n{text}")
    except UnicodeDecodeError as e:
        logging.log(logging.INFO, e)
        await message.answer(
            """
            😔 К сожалению, данный тип файлов не поддерживается!
            
Следите за обновлениями в канале @gptDeep
            """)
    except Exception as e:
        logging.log(logging.INFO, e)


@gptRouter.message(TextCommand([balance_text(), balance_command()]))
async def handle_balance(message: Message):
    gpt_tokens = await tokenizeService.get_tokens(message.from_user.id)

    referral = await referralsService.get_referral(message.from_user.id)
    last_update = datetime.fromisoformat(referral["lastUpdate"].replace('Z', '+00:00'))
    new_date = last_update + timedelta(days=1)
    current_date = datetime.now()

    def get_date():
        if new_date.strftime("%d") == current_date.strftime("%d"):
            return f"Сегодня в {new_date.strftime('%H:%M')}"
        else:
            return f"Завтра в {new_date.strftime('%H:%M')}"

    def get_date_line():
        if gpt_tokens.get("tokens") >= 30000:
            return "🕒 Автопополнение доступно, если меньше *30000* `energy`⚡"

        return f"🕒 Следующее аптопополнение будет: *{get_date()}*   "

    def accept_account():
        if referral['isActivated']:
            return "🔑 Ваш аккаунт подтвержден!"
        else:
            return "🔑 Ваш аккаунт не подтвержден, зайдите через сутки и совершите любое действие!"

    await message.answer(f""" 
👩🏻‍💻 Количество рефералов: *{len(referral['children'])}*
🤑 Ежедневное автопополнение: *{referral['award']}* `energy` ⚡
{accept_account()}
    
💵 Текущий баланс: *{gpt_tokens.get("tokens")}* `energy` ⚡ 
""")


@gptRouter.message(TextCommand([clear_command(), clear_text()]))
async def handle_clear_context(message: Message):
    user_id = message.from_user.id

    hello = await tokenizeService.clear_dialog(user_id)

    if hello.get("status") == 404:
        await message.answer("Диалог уже пуст!")
        return

    if hello is None:
        await message.answer("Ошибка 😔: Не удалось очистить контекст!")
        return

    await message.answer("Контекст диалога успешно очищен! 👌🏻")


@gptRouter.message(TextCommand([change_system_message_command(), change_system_message_text()]))
async def handle_change_model(message: Message):
    is_agreement = await agreement_handler(message)

    if not is_agreement:
        return

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
    is_agreement = await agreement_handler(message)

    if not is_agreement:
        return

    is_subscribe = await is_chat_member(message)

    if not is_subscribe:
        return

    current_model = gptService.get_current_model(message.from_user.id)

    text = """
Выберите модель: 🤖  

Как рассчитывается energy для моделей?

1000 *claude-3-opus* токенов = 6000 `energy` ⚡️
1000 *o1-preview* токенов = 5000 `energy` ⚡️
1000 *GPT-4o* токенов = 1000 `energy` ⚡️
1000 *claude-3.5-sonnet* токенов = 1000 `energy` ⚡️
1000 *o1-mini* токенов = 800 `energy` ⚡️
1000 *claude-3-haiku* токенов = 100 `energy` ⚡️
1000 *GPT-4o-mini* токенов = 70 `energy` ⚡️
1000 *GPT-3.5-turbo* токенов = 50 `energy` ⚡️

1000 *Llama3.1-405B* токенов = 500 `energy` ⚡️

1000 *Llama3.1-70B* токенов = 250 `energy` ⚡️

1000 *Llama-3.1-8B* токенов = 20 `energy` ⚡️
"""

    await message.answer(text=text, reply_markup=create_change_model_keyboard(current_model))
    await asyncio.sleep(0.5)
    await message.delete()


@gptRouter.message(StateCommand(StateTypes.SystemMessageEditing))
async def edit_system_message(message: Message):
    user_id = message.from_user.id

    stateService.set_current_state(user_id, StateTypes.Default)
    await systemMessage.edit_system_message(user_id, message.text)

    await message.answer("Системное сообщение успешно изменено!")
    await message.delete()


@gptRouter.callback_query(StartWithQuery("cancel-system-edit"))
async def cancel_state(callback_query: CallbackQuery):
    system_message = callback_query.data.replace("cancel-system-edit ", "")

    user_id = callback_query.from_user.id

    gptService.set_current_system_message(user_id, system_message)
    stateService.set_current_state(user_id, StateTypes.Default)

    await callback_query.message.delete()
    await callback_query.answer("Успеншно отменено!")


@gptRouter.callback_query(TextCommandQuery(system_messages_list))
async def handle_change_system_message_query(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    system_message = callback_query.data
    current_system_message = gptService.get_current_system_message(user_id)

    if system_message == current_system_message:
        await callback_query.answer(f"Данный режим уже выбран!")
        return

    if system_message == SystemMessages.Custom.value:
        stateService.set_current_state(user_id, StateTypes.SystemMessageEditing)

        await callback_query.message.answer("Напишите ваше системное сообщение", reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [InlineKeyboardButton(text="Отменить изменение ❌",
                                      callback_data=f"cancel-system-edit {current_system_message}"), ],
            ]
        ))

    gptService.set_current_system_message(user_id, system_message)

    await callback_query.message.edit_reply_markup(
        reply_markup=create_system_message_keyboard(system_message)
    )
    if system_message != "question_answer" and current_system_message != "question_answer":
        await tokenizeService.clear_dialog(user_id)

    await asyncio.sleep(0.5)

    await callback_query.answer(f"Режим успешно изменён!")
    await callback_query.message.delete()


@gptRouter.callback_query(
    TextCommandQuery(list(map(lambda model: model.value, list(GPTModels)))))
async def handle_change_model_query(callback_query: CallbackQuery):
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


@gptRouter.message(TextCommand([get_history_command(), get_history_text()]))
async def handle_get_history(message: types.Message):
    is_agreement = await agreement_handler(message)
    if not is_agreement:
        return

    is_subscribe = await is_chat_member(message)
    if not is_subscribe:
        return

    user_id = message.from_user.id

    history = await tokenizeService.history(user_id)

    if history.get("status") == 404:
        await message.answer("История диалога пуста.")
        return

    if history is None:
        await message.answer("Ошибка 😔: Не удалось получить историю диалога!")
        return

    history_data = history.get("response").get("history")

    json_data = json.dumps(history_data, ensure_ascii=False, indent=4)
    file_stream = io.BytesIO(json_data.encode('utf-8'))
    file_stream.name = "dialog_history.json"

    input_file = BufferedInputFile(file_stream.read(), filename=file_stream.name)

    await message.answer_document(input_file)

    await asyncio.sleep(0.5)
    await message.delete()


@gptRouter.message(TextCommand("/bot"))
async def handle_completion(message: Message, batch_messages):
    print(message)

    print(message.chat.type)
    print(message.entities)
    print(message.text)

    # if message.chat.type in ['group', 'supergroup']:
    #
    #     if message.entities is None:
    #         return
    #     mentions = [entity for entity in message.entities if entity.type == 'mention']
    #
    #     if not any(mention.offset <= 0 < mention.offset + mention.length for mention in mentions):
    #         return

    text = ''
    for message in batch_messages:
        text = text + message.text + "\n"
    text = f" {text}\n\n {message.reply_to_message.text}" if message.reply_to_message else text

    await handle_gpt_request(message, text)


@gptRouter.message()
async def handle_completion(message: Message, batch_messages):
    if message.chat.type in ['group', 'supergroup']:

        if message.entities is None:
            return
        mentions = [entity for entity in message.entities if entity.type == 'mention']

        if not any(mention.offset <= 0 < mention.offset + mention.length for mention in mentions):
            return

    text = ''
    for message in batch_messages:
        text = text + message.text + "\n"
    text = f" {text}\n\n {message.reply_to_message.text}" if message.reply_to_message else text

    await handle_gpt_request(message, text)
