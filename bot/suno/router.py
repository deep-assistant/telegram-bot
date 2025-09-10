import logging
import tempfile
import os
import requests

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, CallbackQuery
from pydub import AudioSegment
from pydub.utils import which

from bot.filters import TextCommand, StateCommand, StartWithQuery
from bot.commands import suno_command, suno_text
from bot.empty_prompt import is_empty_prompt
from bot.constants import DEFAULT_ERROR_MESSAGE
from services import StateTypes, stateService, sunoService, tokenizeService

# Указываем путь к ffmpeg для pydub
AudioSegment.converter = which("ffmpeg")
os.environ['PATH'] += ':/usr/bin'

sunoRouter = Router()


async def suno_create_messages(message: Message, generation: dict):
    data = generation.get('data')
    output = data.get('output') if data else None
    audio_url = output.get('audio_url') if output else None

    if audio_url:
        logging.info(f"Suno: получен audio_url: {audio_url}")
        ext = '.flac' if audio_url.endswith('.flac') else '.mp3'
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            response = requests.get(audio_url)
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name
            logging.info(f"Suno: скачан файл {ext} размером {len(response.content)} байт")

        if ext == '.flac':
            base, _ = os.path.splitext(tmp_file_path)
            mp3_path = base + ".mp3"
            try:
                audio = AudioSegment.from_file(tmp_file_path, format="flac")
                audio.export(mp3_path, format="mp3")
                input_file = FSInputFile(mp3_path, filename="output.mp3")
                await message.answer_document(document=input_file, caption="Ваша сгенерированная композиция (mp3)!")
                logging.info(f"Suno: успешно отправлен mp3 файл")
            except Exception as e:
                logging.error(f"Ошибка при конвертации или отправке аудио: {e}")
                await message.answer("Произошла ошибка при обработке аудиофайла.")
            finally:
                if mp3_path and isinstance(mp3_path, str):
                    if os.path.exists(mp3_path):
                        logging.info(f"Удаляю mp3_path: {mp3_path}")
                        os.remove(mp3_path)
                if tmp_file_path and isinstance(tmp_file_path, str):
                    if os.path.exists(tmp_file_path):
                        logging.info(f"Удаляю tmp_file_path: {tmp_file_path}")
                        os.remove(tmp_file_path)
        else:
            try:
                input_file = FSInputFile(tmp_file_path, filename="output.mp3")
                await message.answer_document(document=input_file, caption="Ваша сгенерированная композиция (mp3)!")
                logging.info(f"Suno: успешно отправлен mp3 файл")
            except Exception as e:
                logging.error(f"Ошибка при отправке mp3: {e}")
                await message.answer("Произошла ошибка при отправке аудиофайла.")
            finally:
                if tmp_file_path and isinstance(tmp_file_path, str):
                    if os.path.exists(tmp_file_path):
                        logging.info(f"Удаляю tmp_file_path: {tmp_file_path}")
                        os.remove(tmp_file_path)
    else:
        logging.error(f"Suno: нет audio_url. generation={generation}")
        status = data.get('status') if data else 'unknown'
        error_info = data.get('error', {}) if data else {}
        
        if status == 'failed' and error_info:
            # Use human-readable error message for failed tasks
            human_readable_error = sunoService.get_human_readable_error(error_info)
            await message.answer(human_readable_error)
        else:
            # Fallback for other cases
            error_message = error_info.get('message', 'Неизвестная ошибка')
            await message.answer(
                f"❌ Не удалось получить аудиофайл от Suno.\n\n"
                f"Статус: {status}\n"
                f"Ошибка: {error_message}\n\n"
                f"Попробуйте позже или измените запрос."
            )

    await message.answer(
        text="Cгенерировать Suno еще? 🔥",
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Сгенерировать 🔥",
                        callback_data="suno-generate"
                    )
                ]
            ],
        )
    )


@sunoRouter.message(StateCommand(StateTypes.Suno))
async def suno_generate_handler(message: Message):
    user_id = message.from_user.id

    try:
        if not stateService.is_suno_state(user_id):
            return

        tokens = await tokenizeService.get_tokens(user_id)
        if tokens.get("tokens", 0) < 0:
            await message.answer("""
У вас не хватает *⚡️*. 😔

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!       
""")
            stateService.set_current_state(user_id, StateTypes.Default)
            return

        if is_empty_prompt(message.text):
            await message.answer(
                "🚫 В вашем запросе отсутствует описание музыкальной композиции 🎵. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-suno-generate"
                            )
                        ]
                    ],
                )
            )
            return

        if len(message.text) > 200:
            await message.answer(
                """Описание музыкальной композиции 🎵 *не может быть более 200 символов* для Suno.

Пожалуйста, попробуйте промт короче.
""",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-suno-generate"
                            )
                        ],
                    ],
                )
            )
            return

        # Сохраняем тему и переходим к запросу стиля
        sunoService.store_user_data(str(user_id), topic=message.text)
        stateService.set_current_state(user_id, StateTypes.SunoStyle)

        await message.answer(
            text="""Отлично! Теперь укажите *стиль* музыкальной композиции 🎵.

Например: pop, rock, jazz, classical, electronic, folk, country, blues, hip-hop, reggae, latin, ambient, techno, house, r&b, soul, metal, punk, indie, alternative и другие.

*Не более 50 символов*.
""",
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отмена ❌",
                            callback_data="cancel-suno-generate"
                        )
                    ],
                ]
            ),
        )

    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to process Suno topic: {e}")
        stateService.set_current_state(user_id, StateTypes.Default)
        return


@sunoRouter.message(StateCommand(StateTypes.SunoStyle))
async def suno_style_handler(message: Message):
    user_id = message.from_user.id

    try:
        if not stateService.is_suno_style_state(user_id):
            return

        if is_empty_prompt(message.text):
            await message.answer(
                "🚫 В вашем запросе отсутствует стиль музыкальной композиции 🎵. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-suno-generate"
                            )
                        ]
                    ],
                )
            )
            return

        if len(message.text) > 50:
            await message.answer(
                """Стиль музыкальной композиции 🎵 *не может быть более 50 символов*.

Пожалуйста, попробуйте короче.
""",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-suno-generate"
                            )
                        ],
                    ],
                )
            )
            return

        # Получаем сохраненные данные пользователя
        user_data = sunoService.get_user_data(str(user_id))
        topic = user_data.get('topic', '')
        style = message.text.strip()

        if not topic:
            await message.answer("Произошла ошибка: тема песни не найдена. Попробуйте начать заново.")
            stateService.set_current_state(user_id, StateTypes.Default)
            sunoService.clear_user_data(str(user_id))
            return

        stateService.set_current_state(user_id, StateTypes.Default)

        wait_message = await message.answer(
            f"**⌛️Ожидайте генерацию...**\nТема: {topic}\nСтиль: {style}\nПримерное время ожидания: *3-5 минут*.\nМожете продолжать работать с ботом."
        )

        await message.bot.send_chat_action(message.chat.id, "typing")

        async def task_id_get(task_id: str):
            await message.answer(f"`1:suno:{task_id}:generate`")
            await message.answer(
                f"""Это ID вашей генерации.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.
                                
Вы также получите результат генерации по готовности.
"""
            )

        generation = await sunoService.generate_suno(topic, style, task_id_get)

        # Check if generation failed or returned no data
        if not generation or not generation.get('data'):
            await message.answer(
                "❌ Произошла ошибка при генерации музыки. Возможные причины:\n"
                "• Сервис Diffrhythm временно недоступен\n"
                "• Превышено время ожидания (15 минут)\n"
                "• Проблемы с форматом лирики\n\n"
                "Попробуйте позже или измените тему/стиль песни."
            )
            sunoService.clear_user_data(str(user_id))
            return
            
        status = generation.get('data', {}).get('status')
        
        # Handle failed generations with proper error messages
        if status == "failed":
            error_info = generation.get('data', {}).get('error', {})
            if error_info:
                human_readable_error = sunoService.get_human_readable_error(error_info)
                await message.answer(human_readable_error)
            else:
                await message.answer("❌ Генерация завершилась с ошибкой. Попробуйте позже или измените описание.")
            sunoService.clear_user_data(str(user_id))
            return

        # Handle completed generations
        if status == "completed":
            await suno_create_messages(message, generation)
            await tokenizeService.update_token(user_id, 5700, "subtract")
            await message.answer(
                f"""
🤖 Затрачено на генерацию музыкальной композиции *Suno*: *5700*

❔ /help - Информация по ⚡️
"""
            )
        else:
            await message.answer(
                "⚡️ Энергия не была списана, так как генерация не завершилась успешно."
            )

        await wait_message.delete()

        # Очищаем временные данные
        sunoService.clear_user_data(str(user_id))

    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to generate Suno: {e}")
        stateService.set_current_state(user_id, StateTypes.Default)
        sunoService.clear_user_data(str(user_id))
        return


@sunoRouter.message(TextCommand([suno_command(), suno_text()]))
async def suno_prepare_handler(message: Message):
    user_id = message.from_user.id
    await enter_suno_state(user_id, message)


@sunoRouter.callback_query(StartWithQuery("suno-generate"))
async def suno_prepare_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await enter_suno_state(user_id, callback_query.message)


@sunoRouter.callback_query(StartWithQuery("cancel-suno-generate"))
async def cancel_state(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    stateService.set_current_state(user_id, StateTypes.Default)
    sunoService.clear_user_data(str(user_id))
    await callback_query.message.delete()
    await callback_query.answer("Режим генерации музыки в Suno успешно отменён!")


async def enter_suno_state(user_id, message: Message):
    stateService.set_current_state(user_id, StateTypes.Suno)

    await message.answer(
        text="""*Активирован режим* генерации музыки в *Suno*.

*Следующее ваше сообщение будет интерпретировано как тема песни* для Suno.

После указания темы вы сможете выбрать стиль музыкальной композиции.

Генерация будет стоить *5700⚡️*.

Опишите в следующем сообщении *тему* музыкальной композиции 🎵 (*не более 200 символов*), которую вы хотите сгенерировать или отмените если передумали.
""",
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Отмена ❌",
                        callback_data="cancel-suno-generate"
                    )
                ],
            ]
        ),
    )
