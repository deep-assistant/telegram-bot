from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup

from bot.filters import TextCommand, StateCommand, StartWithQuery
from bot.suno.command_types import suno_command, suno_text
from services import StateTypes, stateService, sunoService, tokenizeService

sunoRouter = Router()


async def suno_create_messages(message, generation):
    result = list(generation['data']['clips'].values())[0]

    await message.answer_photo(
        photo=result["image_large_url"],
        caption=f"""
    Текст *«{result["title"]}»*

    {result["metadata"]["prompt"]}
    """)

    await message.answer_document(document=result["audio_url"])
    await message.answer_video(video=result["video_url"])
    await message.answer(text="Cгенерировать Suno еще? 🔥", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Сгенерировать 🔥",
                    callback_data="suno-generate"
                )
            ]
        ],
    ))


@sunoRouter.message(StateCommand(StateTypes.Suno))
async def suno_generate_handler(message: Message):
    stateService.set_current_state(message.from_user.id, StateTypes.Default)

    wait_message = await message.answer(
        "**⌛️Ожидайте генерацию...** Примерное время ожидания 30-50 секунд. \nМожете продолжать работать с ботом.")

    await message.bot.send_chat_action(message.chat.id, "typing")

    async def task_id_get(task_id: str):
        await message.answer(f"""
ID вашей генерации: `1:suno:{task_id}:generate`.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации ⚡️.
""")

    generation = await sunoService.generate_suno(message.text, task_id_get)

    await suno_create_messages(message, generation)

    await tokenizeService.update_token(message.from_user.id, 5000, "subtract")
    await message.answer(f"""
🤖 Затрачено на генерацию  5000⚡️

❔ /help - Информация по ⚡️
    """)

    await wait_message.delete()


@sunoRouter.message(TextCommand([suno_command(), suno_text()]))
async def suno_prepare_handler(message: Message):
    stateService.set_current_state(message.from_user.id, StateTypes.Suno)

    await message.answer("Напишите какую песню хотите создать.🎵 \nМожете передать тему или текст песни: ")


@sunoRouter.callback_query(StartWithQuery("suno-generate"))
async def suno_prepare_handler(callback: CallbackQuery):
    stateService.set_current_state(callback.message.from_user.id, StateTypes.Suno)

    await callback.message.answer("Напишите какую песню хотите создать.🎵 \nМожете передать тему или текст песни: ")
