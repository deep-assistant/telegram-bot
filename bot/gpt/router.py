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
from aiogram.utils.serialization import deserialize_telegram_object_to_python
from openai import OpenAI

from bot.agreement import agreement_handler
from bot.filters import TextCommand, Document, Photo, TextCommandQuery, Voice, Audio, StateCommand, StartWithQuery, \
    Video
from bot.gpt import change_model_command
from bot.commands import change_system_message_command, change_system_message_text, change_model_text, \
    balance_text, balance_command, clear_command, clear_text, get_history_command, get_history_text
from bot.gpt.system_messages import get_system_message, system_messages_list, \
    create_system_message_keyboard
from bot.gpt.utils import is_chat_member, send_markdown_message, get_tokens_message, \
    create_change_model_keyboard, checked_text
from bot.utils import include
from bot.utils import send_photo_as_file
from bot.constants import DIALOG_CONTEXT_CLEAR_FAILED_DEFAULT_ERROR_MESSAGE
from config import TOKEN, GO_API_KEY, PROXY_URL
from services import gptService, GPTModels, completionsService, tokenizeService, referralsService, stateService, \
    StateTypes, systemMessage
from services.gpt_service import SystemMessages
from services.image_utils import format_image_from_request
from services.utils import async_post, async_get

gptRouter = Router()

questionAnswer = False

# Queue infrastructure for batching messages
queues: dict[tuple[int, int], asyncio.Queue] = {}
locks: dict[tuple[int, int], asyncio.Lock] = {}
last_message_times: dict[tuple[int, int], float] = {}
PRIVATE_TIMEOUT = 10   # seconds
GROUP_TIMEOUT = 30    # seconds

async def produce_message(message: Message):
    """Producer: Add message to queue and update last message time."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    key = (user_id, chat_id)
    
    is_forwarded = message.forward_date is not None
    logging.info(f"Producing message - User: {user_id}, Chat: {chat_id}, Forwarded: {is_forwarded}, Text: {message.text}")
    
    lock = locks.setdefault(key, asyncio.Lock())
    
    async with lock:
        if key not in queues:
            queues[key] = asyncio.Queue()
            logging.info(f"Created new queue for key: {key}")
        await queues[key].put(message)  # Queue handles any message type
        last_message_times[key] = asyncio.get_event_loop().time()
        logging.info(f"Message queued - Key: {key}, Queue size: {queues[key].qsize()}")

async def consumer_task():
    """Consumer: Process queued messages after timeout."""
    while True:
        current_time = asyncio.get_event_loop().time()
        keys = list(queues.keys())

        # logging.info(f"Consumer tick - Active queues: {len(keys)}")
        
        for key in keys:
            user_id, chat_id = key
            last_time = last_message_times.get(key, 0)
            timeout = PRIVATE_TIMEOUT if chat_id > 0 else GROUP_TIMEOUT  # Positive chat_id = private
            
            if current_time - last_time >= timeout and key in queues:
                lock = locks.get(key, asyncio.Lock())
                messages = []
                async with lock:
                    if key not in queues:
                        continue
                    while not queues[key].empty():
                        msg = await queues[key].get()
                        is_forwarded = msg.forward_date is not None
                        messages.append(msg)
                        logging.info(f"Dequeued message - User: {msg.from_user.id}, Forwarded: {is_forwarded}, Text: {msg.text}")
                    if not messages:
                        continue
                    if queues[key].empty():
                        logging.info(f"Queue emptied for key: {key}")
                        del queues[key]
                        del last_message_times[key]
                        del locks[key]
                
                # Process batched messages with new handler
                await handle_messages(messages)
        
        await asyncio.sleep(1)

# Start consumer task on bot startup
def start_consuming_gpt_messages():
    asyncio.create_task(consumer_task())

async def answer_markdown_file(message: Message, md_content: str):
    file_path = f"markdown_files/{uuid.uuid4()}.md"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    await message.answer_document(FSInputFile(file_path), caption="Сообщение в формате markdown")

    os.remove(file_path)


def detect_model(model: str):
    if model is None:
        return None
    
    for model_enum in GPTModels:
        if model_enum.value in model:
            return model_enum.value

    if "auto" in model:
        return GPTModels.GPT_Auto.value
    if "deepseek-r1" in model:
        return GPTModels.DeepSeek_Reasoner.value
    if "gpt-4-gizmo" in model:
        return GPTModels.GPT_4_Unofficial.value
    if "Llama-3.1-405B" in model:
        return GPTModels.Llama3_1_405B.value
    if "Llama-3.1-70B" in model:
        return GPTModels.Llama3_1_70B.value
    if "Llama-3.1-8B" in model:
        return GPTModels.Llama3_1_8B.value
    if "gpt-3.5-turbo" in model:
        return GPTModels.GPT_3_5.value
    if "gpt-4o-plus" in model:
        return GPTModels.GPT_4o
        
    return None

async def query_gpt_with_content(user_id: int, content: list | str, bot_model, gpt_model, system_message):
    try:
        # Convert content to string with --- delimiters if it's a list
        if isinstance(content, list):
            content_str = ""
            for item in content:
                if item["type"] == "text":
                    content_str += item["text"] + "\n---\n"
                elif item["type"] == "image_url":
                    content_str += f"Image: {item['image_url']['url']}\n---\n"
            content = content_str.rstrip("---\n")

        system_message_processed = get_system_message(system_message)
        if system_message_processed == "question-answer":
            questionAnswer = True
        else:
            questionAnswer = False

        print(bot_model, 'bot_model')
        print(gpt_model, 'gpt_model')
        print(content, 'content')
        print(system_message_processed, 'system_message_processed')

        answer = await completionsService.query_chatgpt(
            user_id,
            content,
            system_message_processed,
            gpt_model,
            bot_model,
            questionAnswer,
        )

        print(json.dumps(answer, indent=4))

        requested_gpt_model = gpt_model

        print(requested_gpt_model, 'requested_gpt_model')

        detected_requested_gpt_model = detect_model(requested_gpt_model)

        print(detected_requested_gpt_model, 'detected_requested_gpt_model')

        responded_gpt_model = answer.get("model")

        print(responded_gpt_model, 'responded_gpt_model')

        detected_responded_gpt_model = detect_model(responded_gpt_model)

        print(detected_responded_gpt_model, 'detected_responded_gpt_model')

        if not answer.get("success"):
            return None

        return {"answer": answer, "detected_requested": detected_requested_gpt_model, "detected_responded": detected_responded_gpt_model}
    except Exception as e:
        print(e)
        return None

async def handle_gpt_request(message: Message, text: str):
    message_loading = await message.answer("**⌛️Ожидайте ответ...**")

    try:
        is_agreement = await agreement_handler(message)

        if not is_agreement:
            await message_loading.delete()
            return

        is_subscribe = await is_chat_member(message)

        if not is_subscribe:
            await message_loading.delete()
            return
        
        user_id = message.from_user.id
        if not stateService.is_default_state(user_id):
            await message_loading.delete()
            return

        gpt_tokens_before = await tokenizeService.get_tokens(user_id)

        if gpt_tokens_before.get("tokens", 0) <= 0:
            await message.answer(
                text=f"""
У вас не хватает *⚡️*. 😔

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс 
/referral - 👥 Пригласить друга, чтобы получить бесплатно *⚡️*!
/model - 🛠️ Сменить модель
""")
            await message_loading.delete()
            return

        bot_model = gptService.get_current_model(user_id)
        gpt_model = gptService.get_mapping_gpt_model(user_id)
        chat_id = message.chat.id
        await message.bot.send_chat_action(chat_id, "typing")
        system_message = gptService.get_current_system_message(user_id)

        result = await query_gpt_with_content(user_id, text, bot_model, gpt_model, system_message)
        if result:
            format_text = format_image_from_request(result["answer"].get("response"))
            image = format_text["image"]
            messages = await send_markdown_message(message, format_text["text"])
            if len(messages) > 1:
                await answer_markdown_file(message, format_text["text"])
            if image is not None:
                await message.answer_photo(image)
                await send_photo_as_file(message, image, "Вот картинка в оригинальном качестве")
            await asyncio.sleep(0.5)
            await message_loading.delete()

            gpt_tokens_after = await tokenizeService.get_tokens(user_id)
            tokens_message_text = get_tokens_message(
                gpt_tokens_before.get("tokens", 0) - gpt_tokens_after.get("tokens", 0), 
                gpt_tokens_after.get("tokens", 0), 
                result["detected_requested"], 
                result["detected_responded"]
            )
            token_message = await message.answer(tokens_message_text)
            if message.chat.type in ['group', 'supergroup']:
                await asyncio.sleep(2)
                await token_message.delete()
        else:
            await message_loading.delete()
    except Exception as e:
        print(e)
        await message_loading.delete()

async def get_photos_links(message, photos):
    images = []

    for photo in photos:
        file_info = await message.bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        images.append({"type": "image_url", "image_url": {"url": file_url}})

    return images


# @gptRouter.message(Video())
# async def handle_image(message: Message):
#     print(message.video)

# @gptRouter.message(Photo())
# async def handle_image(message: Message, album):
#     if message.chat.type in ['group', 'supergroup']:
#         if message.entities is None:
#             return

#         # Получаем список всех сущностей типа 'mention'
#         mentions = [
#             entity for entity in message.entities if entity.type == 'mention'
#         ]

#         # Проверяем, упомянут ли бот
#         if not any(
#             mention.offset <= 0 < mention.offset + mention.length and
#             message.text[mention.offset + 1:mention.offset + mention.length] == 'DeepGPTBot'
#             for mention in mentions
#         ):
#             return
#     photos = []

#     for item in album:
#         photos.append(item.photo[-1])

#     user_id = message.from_user.id

#     if not stateService.is_default_state(user_id):
#         return

#     tokens = await tokenizeService.get_tokens(user_id)
#     if tokens.get("tokens") < 0:
#         await message.answer("""
# У вас не хватает *⚡️*. 😔

# /balance - ✨ Проверить Баланс
# /buy - 💎 Пополнить баланс
# /referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!       
# """)
#         stateService.set_current_state(user_id, StateTypes.Default)
#         return

#     is_subscribe = await is_chat_member(message)

#     if not is_subscribe:
#         return

#     text = "Опиши" if message.caption is None else message.caption

#     await message.bot.send_chat_action(message.chat.id, "typing")

#     content = await get_photos_links(message, photos)

#     content.append({"type": "text", "text": text})

#     await handle_gpt_request(message, content)


async def handle_messages(messages: list[Message]):
    """Handle batched messages with a single loading message."""
    last_message = messages[-1]  # Use the last message for replying
    user_id = last_message.from_user.id
    
    logging.info(f"Handling {len(messages)} messages for User: {user_id}")
    for msg in messages:
        is_forwarded = msg.forward_date is not None
        logging.info(f"Message in batch - User: {msg.from_user.id}, Forwarded: {is_forwarded}, Text: {msg.text}")
    
    # Single loading message
    message_loading = await last_message.answer("**⌛️Ожидайте ответ...**")
    
    try:
        is_agreement = await agreement_handler(last_message)
        if not is_agreement:
            await message_loading.delete()
            return

        is_subscribe = await is_chat_member(last_message)
        if not is_subscribe:
            await message_loading.delete()
            return
        
        if not stateService.is_default_state(user_id):
            await message_loading.delete()
            return

        gpt_tokens_before = await tokenizeService.get_tokens(user_id)
        if gpt_tokens_before.get("tokens", 0) <= 0:
            await last_message.answer(
                text=f"""
У вас не хватает *⚡️*. 😔

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс 
/referral - 👥 Пригласить друга, чтобы получить бесплатно *⚡️*!
/model - 🛠️ Сменить модель
""")
            await message_loading.delete()
            return
        
        bot_model = gptService.get_current_model(user_id)
        gpt_model = gptService.get_mapping_gpt_model(user_id)
        chat_id = last_message.chat.id
        await last_message.bot.send_chat_action(chat_id, "typing")
        system_message = gptService.get_current_system_message(user_id)

        # Process all messages in parallel
        async def process_message(msg):
            content = []
            user_info = f"From: {msg.from_user.full_name} (ID: {msg.from_user.id})"
            prefix = user_info
            if msg.forward_from or msg.forward_from_chat:
                forward_info = (
                    f"Forwarded from: {msg.forward_from.full_name} (ID: {msg.forward_from.id})" if msg.forward_from
                    else f"Forwarded from chat: {msg.forward_from_chat.title} (ID: {msg.forward_from_chat.id})"
                )
                prefix = f"{user_info}\n{forward_info}"

            if msg.reply_to_message:
                # reply_user = f"Reply to: {msg.reply_to_message.from_user.full_name} (ID: {msg.reply_to_message.from_user.id})"
                # content.append({"type": "text", "text": f"{reply_user}\nReplied to: {msg.reply_to_message.text}"})

                processed_reply = await process_message(msg.reply_to_message)

                reply_to_message_text = processed_reply[0].get('text')

                # add > quote symbols to each line

                reply_to_message_text = reply_to_message_text.replace('\n', '\n> ')

                prefix = f"{prefix}\nReplied to:\n> {reply_to_message_text}"

            if msg.text:
                content.append({"type": "text", "text": f"{prefix}\n\n {msg.text}"})
            
            if msg.photo:
                photos = [msg.photo[-1]] if not hasattr(msg, 'album') else [item.photo[-1] for item in msg.album]
                photo_links = await get_photos_links(msg, photos)
                text = "Опиши" if msg.caption is None else msg.caption
                photo_content = photo_links + [{"type": "text", "text": text}]
                photo_answer = await query_gpt_with_content(user_id, photo_content, bot_model, gpt_model, system_message)
                if photo_answer:
                    content.append({"type": "text", "text": f"{user_info}\nPhoto Description: {photo_answer.get('answer').get('response')}"})
            
            if msg.voice or msg.audio:
                messageData = msg.voice or msg.audio
                file = await msg.bot.get_file(messageData.file_id)
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
                voice_response = await transcribe_voice(msg.from_user.id, file_url)
                if voice_response.get("success"):
                    content.append({"type": "text", "text": f"{user_info}\nTranscribed Voice/Audio: {voice_response.get('text')}"})
            
            if msg.document:
                doc_text = await process_document(msg.document, msg.bot)
                caption = msg.caption or "No caption"
                content.append({"type": "text", "text": f"{user_info}\nDocument: {msg.document.file_name}\nCaption: {caption}\nContent: {doc_text}"})
            
            return content

        results = await asyncio.gather(*(process_message(msg) for msg in messages))
        
        # Combine results
        final_content = []
        for result in results:
            final_content.extend(result)
        
        # Query GPT with combined content
        if final_content:
            result = await query_gpt_with_content(user_id, final_content, bot_model, gpt_model, system_message)
            if result:
                format_text = format_image_from_request(result["answer"].get("response"))
                image = format_text["image"]
                messages = await send_markdown_message(last_message, format_text["text"])
                if len(messages) > 1:
                    await answer_markdown_file(last_message, format_text["text"])
                if image is not None:
                    await last_message.answer_photo(image)
                    await send_photo_as_file(last_message, image, "Вот картинка в оригинальном качестве")
                await asyncio.sleep(0.5)
                await message_loading.delete()

                gpt_tokens_after = await tokenizeService.get_tokens(user_id)
                tokens_message_text = get_tokens_message(
                    gpt_tokens_before.get("tokens", 0) - gpt_tokens_after.get("tokens", 0),
                    gpt_tokens_after.get("tokens", 0),
                    result["detected_requested"],
                    result["detected_responded"]
                )
                token_message = await last_message.answer(tokens_message_text)
                if last_message.chat.type in ['group', 'supergroup']:
                    await asyncio.sleep(2)
                    await token_message.delete()
            else:
                await message_loading.delete()
        else:
            await last_message.answer("No valid content to process.")
            await message_loading.delete()
    
    except Exception as e:
        print(f"Error in handle_messages: {e}")
        await message_loading.delete()

@gptRouter.message(Video())
async def handle_video(message: Message):
    is_forwarded = message.forward_date is not None
    logging.info(f"Video message received - User: {message.from_user.id}, Forwarded: {is_forwarded}")
    print(message.video)

@gptRouter.message(Photo())
async def handle_image(message: Message):
    is_forwarded = message.forward_date is not None
    logging.info(f"Photo message received - User: {message.from_user.id}, Forwarded: {is_forwarded}")
    if message.chat.type in ['group', 'supergroup']:
        if message.entities is None:
            return
        mentions = [entity for entity in message.entities if entity.type == 'mention']
        if not any(mention.offset <= 0 < mention.offset + mention.length and
                  message.text[mention.offset + 1:mention.offset + mention.length] == 'DeepGPTBot'
                  for mention in mentions):
            return
    await produce_message(message)


async def transcribe_voice_sync(user_id: str, voice_file_url: str):
    token = await tokenizeService.get_token(user_id)

    voice_response = await async_get(voice_file_url)
    if voice_response.status_code == 200:
        voice_data = voice_response.content

        client = OpenAI(
            api_key=token["id"],
            base_url=f"{PROXY_URL}/v1/"
        )

        transcription = client.audio.transcriptions.create(file=('audio.ogg', voice_data, 'audio/ogg'),
                                                           model="whisper-1", language="ru")

        print(transcription.duration)
        print( transcription.text)
        return {"success": True, "text": transcription.text, 'energy': int(transcription.duration*15)}
    else:
        return {"success": False, "text": f"Error: Голосовое сообщение не распознано"}


executor = ThreadPoolExecutor()


async def transcribe_voice(user_id: int, voice_file_url: str):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(executor, transcribe_voice_sync, user_id, voice_file_url)
    return await response


@gptRouter.message(Voice())
@gptRouter.message(Audio())
async def handle_voice(message: Message):
    is_forwarded = message.forward_date is not None
    logging.info(f"Voice/Audio message received - User: {message.from_user.id}, Forwarded: {is_forwarded}")
    if message.chat.type in ['group', 'supergroup']:
        if message.entities is None:
            return
        mentions = [entity for entity in message.entities if entity.type == 'mention']
        if not any(mention.offset <= 0 < mention.offset + mention.length for mention in mentions):
            return
    await produce_message(message)

#     user_id = message.from_user.id

#     if not stateService.is_default_state(user_id):
#         return
        
#     tokens = await tokenizeService.get_tokens(user_id)
#     if tokens.get("tokens") < 0:
#         await message.answer("""
# У вас не хватает *⚡️*. 😔

# /balance - ✨ Проверить Баланс
# /buy - 💎 Пополнить баланс
# /referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!       
# """)
#         stateService.set_current_state(user_id, StateTypes.Default)
#         return

#     is_subscribe = await is_chat_member(message)

#     if not is_subscribe:
#         return


#     if message.voice is not None:
#         messageData = message.voice
#     else: 
#         messageData = message.audio


#     duration = messageData.duration
#     voice_file_id = messageData.file_id
#     file = await message.bot.get_file(voice_file_id)
#     file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

#     response_json = await transcribe_voice(message.from_user.id, file_url)

#     if response_json.get("success"):
#         await message.answer(f"""
# 🎤 Обработка аудио затратила `{response_json.get("energy")}`⚡️ 

# ❔ /help - Информация по ⚡️
# """)

        
#         current_state = stateService.get_current_state(message.from_user.id) 
#         print(current_state, 'current_state')
#         print(StateTypes.Transcribe, 'StateTypes.TranscribeStateTypes.Transcribe')
#         if current_state == StateTypes.Transcribe:  
#             await message.reply(response_json.get('text'))  
#             return
            
#         await handle_gpt_request(message, response_json.get('text'))
#         return

#     await message.answer(response_json.get('text'))

@gptRouter.message(Document())
async def handle_document(message: Message):
    is_forwarded = message.forward_date is not None
    logging.info(f"Document message received - User: {message.from_user.id}, Forwarded: {is_forwarded}")
    if message.chat.type in ['group', 'supergroup']:
        if message.caption_entities is None:
            return
        mentions = [entity for entity in message.caption_entities if entity.type == 'mention']
        if not any(mention.offset <= 0 < mention.offset + mention.length for mention in mentions):
            return
    await produce_message(message)

#         try:
#         user_document = message.document if message.document else None
#         if user_document:
#             with NamedTemporaryFile(delete=False) as temp_file:
#                 await message.bot.download(user_document, temp_file.name)
#             async with aiofiles.open(temp_file.name, 'r', encoding='utf-8') as file:
#                 text = await file.read()
#                 caption = message.caption if message.caption is not None else ""
#                 await handle_gpt_request(message, f"{caption}\n{text}")
#     except UnicodeDecodeError as e:
#         await message.answer("""😔 К сожалению, данный тип файлов не поддерживается!
            
# Следите за обновлениями в канале @gptDeep или напишите нам в чате @deepGPT""")
#         logging.error(f"Failed to process document, a file is not supported: {e}")
#     except Exception as e:
#         logging.error(f"Failed to process document: {e}")


async def process_document(document, bot):
    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            await bot.download(document, temp_file.name)
        async with aiofiles.open(temp_file.name, 'r', encoding='utf-8') as file:
            text = await file.read()
        return text
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"UnicodeDecodeError: failed to read file '{document.file_name}' - {e}")
    except Exception as e:
        raise Exception(f"Error: failed to process file '{document.file_name}' - {e}")


def is_valid_group_message(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        if message.caption_entities is None:
            return False
        mentions = [entity for entity in message.caption_entities if entity.type == 'mention']
        return any(mention.offset <= 0 < mention.offset + mention.length for mention in mentions)
    return True


async def handle_documents(message: Message, documents):
    bot = message.bot
    combined_text = ""
    errors = []

    for document in documents:
        if document.mime_type == 'text/plain':  # Check for valid text documents
            try:
                text = await process_document(document, bot)
                combined_text += f"\n\n=== Файл: {document.file_name} ===\n{text}"
            except Exception as e:
                errors.append(str(e))
        else:
            errors.append(f"Неподдерживаемый тип файла для '{document.file_name}'")

    caption = message.caption if message.caption else ""
    result_text = f"{caption}\n{combined_text}"

    if errors:
        error_text = "\n\n".join(errors)
        result_text += f"\n\n😔 К сожалению, при обработке файлов произошли ошибки:\n{error_text}\n\nСледите за обновлениями в канале @gptDeep"

    await handle_gpt_request(message, result_text)


# Handler for single document
@gptRouter.message(Document())
async def handle_document(message: Message):
    # Check message validity in group/supergroup
    if not is_valid_group_message(message):
        return

    # Process single document
    user_document = message.document if message.document else None
    if user_document:
        await handle_documents(message, [user_document])


# Handler for media group (multiple documents)


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
            return "🕒 Автопополнение доступно, если меньше *30000*⚡️"

        return f"🕒 Следующее аптопополнение будет: *{get_date()}*   "

    def accept_account():
        if referral['isActivated']:
            return "🔑 Ваш аккаунт подтвержден!"
        else:
            return "🔑 Ваш аккаунт не подтвержден, зайдите через сутки и совершите любое действие!"

    await message.answer(f""" 
👩🏻‍💻 Количество рефералов: *{len(referral['children'])}*
🤑 Ежедневное автопополнение 🔋: *{referral['award']}⚡️*
{accept_account()}
    
🔋 - ежедневное автопополнение работает, если на балансе меньше *30 000⚡️*

💵 Текущий баланс: *{gpt_tokens.get("tokens")}⚡️*
""")


@gptRouter.message(TextCommand([clear_command(), clear_text()]))
async def handle_clear_context(message: Message):
    user_id = message.from_user.id

    try:
        response = await tokenizeService.clear_dialog(user_id)

        if not response.get("status"):
            await message.answer("Диалог уже пуст!")
            return

        if response is None:
            await message.answer(DIALOG_CONTEXT_CLEAR_FAILED_DEFAULT_ERROR_MESSAGE)
            logging.error(f"Cannot clear dialog context for user {user_id}, response is None.")
            return
    except Exception as e:
        await message.answer(DIALOG_CONTEXT_CLEAR_FAILED_DEFAULT_ERROR_MESSAGE)
        logging.error(f"Error clearing dialog context for user {user_id}: {e}")
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
    print(current_system_message, 'current_system_message')

    if not include(system_messages_list, current_system_message):
        current_system_message = SystemMessages.Custom.value
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

Как рассчитывается стоимость в ⚡️️ для моделей?

*o3-mini:* 1000 токенов = 800 ⚡️

*o1-preview:* 1000 токенов = 5000 ⚡️
*o1-mini:* 1000 токенов = 800 ⚡️

*deepseek-reasoner:* 1000 токенов = 320 ⚡️
*deepseek-chat:* 1000 токенов = 160 ⚡️

*claude-3-opus:* 1000 токенов = 6000 ⚡️
*claude-3.5-sonnet:* 1000 токенов = 1000 ⚡️
*claude-3-5-haiku:* 1000 токенов = 100 ⚡️

*GPT-4o-unofficial:* 1000 токенов = 1100 ⚡️
*GPT-4o:* 1000 токенов = 1000 ⚡️
*GPT-Auto:* 1000 токенов = 150 ⚡️
*GPT-4o-mini:* 1000 токенов = 70 ⚡️
*GPT-3.5-turbo:* 1000 токенов = 50 ⚡️

*Llama3.1-405B:* 1000 токенов = 500 ⚡️
*Llama3.1-70B:* 1000 токенов = 250 ⚡️
*Llama-3.1-8B:* 1000 токенов = 20 ⚡️

"""

    await message.answer(text=text, reply_markup=create_change_model_keyboard(current_model))
    await asyncio.sleep(0.5)
    await message.delete()


@gptRouter.message(StateCommand(StateTypes.SystemMessageEditing))
async def edit_system_message(message: Message):
    user_id = message.from_user.id

    print('SystemMessageEditingSystemMessageEditingSystemMessageEditing')

    gptService.set_current_system_message(user_id, message.text)
   
    await systemMessage.edit_system_message(user_id, message.text)

    stateService.set_current_state(user_id, StateTypes.Default)

    await asyncio.sleep(0.5)

    await message.answer(f"Режим успешно изменён!")
    await message.delete()



@gptRouter.callback_query(StartWithQuery("cancel-system-edit"))
async def cancel_state(callback_query: CallbackQuery):
    system_message = callback_query.data.replace("cancel-system-edit ", "")

    user_id = callback_query.from_user.id

    gptService.set_current_system_message(user_id, system_message)
    stateService.set_current_state(user_id, StateTypes.Default)

    await callback_query.message.delete()
    await callback_query.answer("Успешно отменено!")


@gptRouter.callback_query(TextCommandQuery(system_messages_list))
async def handle_change_system_message_query(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    system_message = callback_query.data
    current_system_message = gptService.get_current_system_message(user_id)

    if (system_message == current_system_message and system_message != SystemMessages.Custom.value):
        await callback_query.answer(f"Данный режим уже выбран!")
        return

    if system_message == SystemMessages.Custom.value:
        stateService.set_current_state(user_id, StateTypes.SystemMessageEditing)

        await callback_query.message.answer("Напишите ваше системное сообщение", reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена ❌",
                                      callback_data=f"cancel-system-edit {current_system_message}"), ],
            ]
        ))

    if system_message == SystemMessages.Transcribe.value:   
        stateService.set_current_state(user_id, StateTypes.Transcribe)

        await callback_query.message.answer("Режим 'Голос в Текст' включен. Бот будет транскрибировать все следующие аудио") 

    
    print('handle_change_system_message_query', 'system_message', system_message)

    gptService.set_current_system_message(user_id, system_message)

    if system_message != SystemMessages.Transcribe.value and system_message != SystemMessages.Custom.value: 
        stateService.set_current_state(user_id, StateTypes.Default)

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

    print('handle_change_model_query', 'callback_query.data', callback_query.data)

    gpt_model = GPTModels(callback_query.data)

    print('handle_change_model_query', 'gpt_model', gpt_model)

    current_gpt_model = gptService.get_current_model(user_id)

    print('handle_change_model_query', 'current_gpt_model', current_gpt_model)

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

    history_data = history.get("response").get("messages")

    json_data = json.dumps(history_data, ensure_ascii=False, indent=4)
    file_stream = io.BytesIO(json_data.encode('utf-8'))
    file_stream.name = "dialog_history.json"

    input_file = BufferedInputFile(file_stream.read(), filename=file_stream.name)

    await message.answer_document(input_file)

    await asyncio.sleep(0.5)
    await message.delete()



# @gptRouter.message(TextCommand(["/bot", "/bot@DeepGPTBot"]))  # Укажите все возможные варианты
# async def handle_bot_command(message: Message, batch_messages):
#     # Логирование для отладки
#     print(f"Command received: {message.text}")
    
#     # Собираем текст только из текущего сообщения (если batch не нужен)
#     text = message.text or ""
    
#     # Добавляем текст из сообщения, на которое ответили
#     if message.reply_to_message and message.reply_to_message.text:
#         text += f"\n\n{message.reply_to_message.text}"
    
#     await handle_gpt_request(message, text)


@gptRouter.message()
async def handle_completion(message: Message):
    is_forwarded = message.forward_date is not None
    logging.info(f"Default handler - User: {message.from_user.id}, Forwarded: {is_forwarded}, Text: {message.text}")

    # Convert the message object to a Python dict
    message_dict = deserialize_telegram_object_to_python(message)
    # Serialize the dict to a JSON string
    message_json = json.dumps(message_dict, indent=4)
    print(message_json)

    if message.chat.type in ['group', 'supergroup']:
        # Проверяем наличие упоминаний
        if not message.entities:
            return

        # Ищем любое упоминание бота (включая @)
        bot_username = "DeepGPTBot"  # Убедитесь, что username точный (без @)
        mentioned = any(
            entity.type == "mention" 
            and message.text[entity.offset + 1 : entity.offset + entity.length] == bot_username
            for entity in message.entities
        )

        if not mentioned:
            return

    await produce_message(message)