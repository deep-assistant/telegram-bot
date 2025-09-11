from aiogram import Router
from aiogram.types import Message

from bot.filters import TextCommand, Photo, StateCommand, CompositeFilters, PngDocument
from bot.commands import get_remove_background_command
from bot.utils import send_photo_as_file
from config import TOKEN
from services import stateService, StateTypes, imageEditing, tokenizeService

imageEditingRouter = Router()

@imageEditingRouter.message(TextCommand([get_remove_background_command()]))
async def handle_remove_background_start(message: Message):
    await message.answer("Пришлите фотографию или PNG файл (как документ), чтобы удалить фон.")
    stateService.set_current_state(message.from_user.id, StateTypes.ImageEditing)


@imageEditingRouter.message(CompositeFilters([Photo(), StateCommand(StateTypes.ImageEditing)]))
async def handle_remove_background(message: Message, album):
    stateService.set_current_state(message.from_user.id, StateTypes.Default)
    wait_message = await message.answer("**⌛️Ожидайте ответ...**")

    photos = []

    for item in album:
        photos.append(item.photo[-1])

    image = photos[0]

    try:

        file_info = await message.bot.get_file(image.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        result = await imageEditing.remove_background(file_url)

        image_url = result["data"]["task_result"]["task_output"]["image_url"]
        await message.reply_photo(image_url)
        await send_photo_as_file(
            message,
            image_url,
            "Вот картинка в оригинальном качестве",
            ext=".png"
        )

        await tokenizeService.update_token(message.from_user.id, 400, "subtract")
        await message.answer(f"""
🤖 Затрачено на удаление фона изображения 400⚡️

❔ /help - Информация по ⚡️
""")

    except Exception as e:
        print(e)
    finally:
        await wait_message.delete()


@imageEditingRouter.message(CompositeFilters([PngDocument(), StateCommand(StateTypes.ImageEditing)]))
async def handle_remove_background_png(message: Message):
    stateService.set_current_state(message.from_user.id, StateTypes.Default)
    wait_message = await message.answer("**⌛️Ожидайте ответ...**")

    try:
        document = message.document
        file_info = await message.bot.get_file(document.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        result = await imageEditing.remove_background(file_url)

        image_url = result["data"]["task_result"]["task_output"]["image_url"]
        await message.reply_photo(image_url)
        await send_photo_as_file(
            message,
            image_url,
            "Вот картинка в оригинальном качестве",
            ext=".png"
        )

        await tokenizeService.update_token(message.from_user.id, 400, "subtract")
        await message.answer(f"""
🤖 Затрачено на удаление фона изображения 400⚡️

❔ /help - Информация по ⚡️
""")

    except Exception as e:
        print(e)
    finally:
        await wait_message.delete()
