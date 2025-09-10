import logging
import tempfile
import os
import requests

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, CallbackQuery

from bot.filters import TextCommand, StateCommand, StartWithQuery
from bot.commands import video_command, video_text
from bot.empty_prompt import is_empty_prompt
from bot.constants import DEFAULT_ERROR_MESSAGE
from services import StateTypes, stateService, videoService, tokenizeService

videoRouter = Router()


async def video_create_messages(message: Message, generation: dict):
    data = generation.get('data')
    output = data.get('output') if data else None
    video_url = output.get('video_url') if output else None

    if video_url:
        logging.info(f"Video: получен video_url: {video_url}")
        
        # Определяем расширение файла
        ext = '.mp4'
        if video_url.endswith('.mov'):
            ext = '.mov'
        elif video_url.endswith('.webm'):
            ext = '.webm'
            
        try:
            # Скачиваем видеофайл
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                response = requests.get(video_url, timeout=60)
                response.raise_for_status()
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
                logging.info(f"Video: скачан файл {ext} размером {len(response.content)} байт")

            # Отправляем видео
            input_file = FSInputFile(tmp_file_path, filename=f"generated_video{ext}")
            await message.answer_video(
                video=input_file, 
                caption="Ваше сгенерированное видео! 🎬"
            )
            logging.info(f"Video: успешно отправлен видеофайл")
            
        except Exception as e:
            logging.error(f"Ошибка при скачивании или отправке видео: {e}")
            await message.answer(
                f"❌ Произошла ошибка при загрузке видеофайла.\n\n"
                f"Ссылка на видео: {video_url}\n\n"
                f"Попробуйте скачать по ссылке или повторите генерацию."
            )
        finally:
            # Удаляем временный файл
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                logging.info(f"Удаляю tmp_file_path: {tmp_file_path}")
                os.remove(tmp_file_path)
    else:
        logging.error(f"Video: нет video_url. generation={generation}")
        status = data.get('status') if data else 'unknown'
        error_info = data.get('error', {}) if data else {}
        error_message = error_info.get('message', 'Неизвестная ошибка')
        
        await message.answer(
            f"❌ Не удалось получить видеофайл.\n\n"
            f"Статус: {status}\n"
            f"Ошибка: {error_message}\n\n"
            f"Попробуйте позже или измените запрос."
        )

    await message.answer(
        text="Cгенерировать видео еще? 🎬",
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Сгенерировать 🎬",
                        callback_data="video-generate"
                    )
                ]
            ],
        )
    )


@videoRouter.message(StateCommand(StateTypes.Video))
async def video_generate_handler(message: Message):
    user_id = message.from_user.id

    try:
        if not stateService.is_video_state(user_id):
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
                "🚫 В вашем запросе отсутствует описание видео 🎬. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-video-generate"
                            )
                        ]
                    ],
                )
            )
            return

        if len(message.text) > 500:
            await message.answer(
                """Описание видео 🎬 *не может быть более 500 символов*.

Пожалуйста, попробуйте промт короче.
""",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-video-generate"
                            )
                        ],
                    ],
                )
            )
            return

        # Сохраняем промпт и переходим к запросу стиля
        videoService.store_user_data(str(user_id), prompt=message.text)
        stateService.set_current_state(user_id, StateTypes.VideoStyle)

        await message.answer(
            text="""Отлично! Теперь укажите *стиль* видео 🎬.

Доступные стили:
• realistic - реалистичное видео
• cartoon - мультяшный стиль
• anime - аниме стиль
• cinematic - кинематографический стиль
• artistic - художественный стиль

*Не более 50 символов*.
""",
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Реалистичный 📷",
                            callback_data="video-style-realistic"
                        ),
                        InlineKeyboardButton(
                            text="Мультяшный 🎨",
                            callback_data="video-style-cartoon"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Аниме 🎌",
                            callback_data="video-style-anime"
                        ),
                        InlineKeyboardButton(
                            text="Кинематограф 🎭",
                            callback_data="video-style-cinematic"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Художественный 🖼️",
                            callback_data="video-style-artistic"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Отмена ❌",
                            callback_data="cancel-video-generate"
                        )
                    ],
                ]
            ),
        )

    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to process Video prompt: {e}")
        stateService.set_current_state(user_id, StateTypes.Default)
        return


@videoRouter.callback_query(StartWithQuery("video-style-"))
async def video_style_callback_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    style = callback_query.data.replace("video-style-", "")
    
    # Получаем сохраненные данные пользователя
    user_data = videoService.get_user_data(str(user_id))
    prompt = user_data.get('prompt', '')
    
    if not prompt:
        await callback_query.message.answer("Произошла ошибка: описание видео не найдено. Попробуйте начать заново.")
        stateService.set_current_state(user_id, StateTypes.Default)
        videoService.clear_user_data(str(user_id))
        await callback_query.answer()
        return
    
    await process_video_generation(callback_query.message, user_id, prompt, style)
    await callback_query.answer()


@videoRouter.message(StateCommand(StateTypes.VideoStyle))
async def video_style_handler(message: Message):
    user_id = message.from_user.id

    try:
        if not stateService.is_video_style_state(user_id):
            return

        if is_empty_prompt(message.text):
            await message.answer(
                "🚫 В вашем запросе отсутствует стиль видео 🎬. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-video-generate"
                            )
                        ]
                    ],
                )
            )
            return

        if len(message.text) > 50:
            await message.answer(
                """Стиль видео 🎬 *не может быть более 50 символов*.

Пожалуйста, попробуйте короче.
""",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-video-generate"
                            )
                        ],
                    ],
                )
            )
            return

        # Получаем сохраненные данные пользователя
        user_data = videoService.get_user_data(str(user_id))
        prompt = user_data.get('prompt', '')
        style = message.text.strip()

        if not prompt:
            await message.answer("Произошла ошибка: описание видео не найдено. Попробуйте начать заново.")
            stateService.set_current_state(user_id, StateTypes.Default)
            videoService.clear_user_data(str(user_id))
            return

        await process_video_generation(message, user_id, prompt, style)

    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to generate Video: {e}")
        stateService.set_current_state(user_id, StateTypes.Default)
        videoService.clear_user_data(str(user_id))
        return


async def process_video_generation(message: Message, user_id: int, prompt: str, style: str):
    """Общая функция для обработки генерации видео"""
    stateService.set_current_state(user_id, StateTypes.Default)

    wait_message = await message.answer(
        f"**⌛️Ожидайте генерацию...**\nОписание: {prompt}\nСтиль: {style}\nПримерное время ожидания: *5-15 минут*.\nМожете продолжать работать с ботом."
    )

    await message.bot.send_chat_action(message.chat.id, "typing")

    async def task_id_get(task_id: str):
        await message.answer(f"`1:video:{task_id}:generate`")
        await message.answer(
            f"""Это ID вашей генерации.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.
                            
Вы также получите результат генерации по готовности.
"""
        )

    generation = await videoService.generate_video(prompt, style, task_id_get)

    if not generation or not generation.get('data'):
        await message.answer(
            "❌ Произошла ошибка при генерации видео. Возможные причины:\n"
            "• Сервис Kling временно недоступен\n"
            "• Превышено время ожидания (30 минут)\n"
            "• Проблемы с форматом запроса\n\n"
            "Попробуйте позже или измените описание/стиль видео."
        )
        videoService.clear_user_data(str(user_id))
        return

    await video_create_messages(message, generation)

    # Списываем токены только если generation успешна
    status = generation.get('data', {}).get('status')
    if status == "completed":
        await tokenizeService.update_token(user_id, 8000, "subtract")
        await message.answer(
            f"""
🤖 Затрачено на генерацию видео *Kling*: *8000*

❔ /help - Информация по ⚡️
"""
        )
    else:
        await message.answer(
            "⚡️ Энергия не была списана, так как генерация завершилась с ошибкой."
        )

    await wait_message.delete()

    # Очищаем временные данные
    videoService.clear_user_data(str(user_id))


@videoRouter.message(TextCommand([video_command(), video_text()]))
async def video_prepare_handler(message: Message):
    user_id = message.from_user.id
    await enter_video_state(user_id, message)


@videoRouter.callback_query(StartWithQuery("video-generate"))
async def video_prepare_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await enter_video_state(user_id, callback_query.message)


@videoRouter.callback_query(StartWithQuery("cancel-video-generate"))
async def cancel_state(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    stateService.set_current_state(user_id, StateTypes.Default)
    videoService.clear_user_data(str(user_id))
    await callback_query.message.delete()
    await callback_query.answer("Режим генерации видео успешно отменён!")


async def enter_video_state(user_id, message: Message):
    stateService.set_current_state(user_id, StateTypes.Video)

    await message.answer(
        text="""*Активирован режим* генерации видео в *Kling*.

*Следующее ваше сообщение будет интерпретировано как описание видео* для генерации.

После указания описания вы сможете выбрать стиль видео.

Генерация будет стоить *8000⚡️*.

Опишите в следующем сообщении *содержание видео* 🎬 (*не более 500 символов*), которое вы хотите сгенерировать или отмените если передумали.

*Примеры хороших промптов:*
• "Кот играет с мячиком на солнечной лужайке"
• "Машина едет по горной дороге на закате"
• "Танцующие люди на пляже под звездным небом"
""",
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Отмена ❌",
                        callback_data="cancel-video-generate"
                    )
                ],
            ]
        ),
    )