from aiogram import Router
from aiogram.types import Message

from bot.filters import TextCommand, StateCommand
from bot.suno.command_types import suno_command
from services import StateTypes, stateService, sunoService, tokenizeService

sunoRouter = Router()


@sunoRouter.message(StateCommand(StateTypes.Suno))
async def suno_generate_handler(message: Message):
    stateService.set_current_state(message.from_user.id, StateTypes.Default)

    wait_message = await message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 30-50 секунд. \nМожете продолжать работать с ботом.")

    await message.bot.send_chat_action(message.chat.id, "typing")

    generation = await sunoService.generate_suno(message.text)

    result = list(generation['data']['clips'].values())[0]

    await message.answer_photo(
        photo=result["image_large_url"],
        caption=f"""
Текст *«{result["title"]}»*

{result["metadata"]["prompt"]}
""")

    await message.answer_document(document=result["audio_url"])
    await message.answer_video(video=result["video_url"])

    await tokenizeService.update_user_token(message.from_user.id, 5000, "subtract")
    await message.answer(f"""
🤖 Затрачено на генерацию  5000 `energy` ⚡

❔ /help - Информация по `energy` ⚡
    """)

    await wait_message.delete()


@sunoRouter.message(TextCommand([suno_command()]))
async def suno_prepare_handler(message: Message):
    stateService.set_current_state(message.from_user.id, StateTypes.Suno)

    await message.answer("Напишите какую песню хотите создать.🎵 \nМожете передать тему или текст песни: ")
