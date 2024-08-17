from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from bot.filters import StartWith
from bot.images.router import send_variation_image
from bot.suno import suno_create_messages
from bot.utils import send_photo_as_file
from services import imageService, sunoService

taskRouter = Router()


@taskRouter.message(StartWith("1:midjourney:"))
async def handle_midjourney_message(message: Message):
    data = message.text.replace("1:midjourney:", "")
    task_id = data.split(":")[0]
    action = data.split(":")[1]

    task = await imageService.task_fetch(task_id)

    if task['status'] == "finished":
        image = task["task_result"]["discord_image_url"]
        if action == "generate":
            await send_variation_image(
                message,
                image,
                task["task_id"]
            )
        if action == "upscale":
            await message.reply_photo(image)
            await send_photo_as_file(
                message,
                image,
                "Вот выше изображение в оригинальном качестве"
            )
            await message.answer(text="Cгенерировать Midjourney еще? 🔥", reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"Сгенерировать 🔥",
                            callback_data="midjourney-generate"
                        )
                    ]
                ],
            ))

        return

    if task['status'] == "processing":
        await message.answer("⌛️ Задача в процессе!")
        return

    await message.answer("Генерация не удалась. Что-то пошло не так! 😔")


@taskRouter.message(StartWith("1:suno:"))
async def handle_syno_message(message: Message):
    data = message.text.replace("1:suno:", "")
    task_id = data.split(":")[0]

    task = await sunoService.task_fetch(task_id)

    print(task)
    status = task["data"]["status"]

    if status == "completed":
        await suno_create_messages(message, task)
        return

    if status == "processing":
        await message.answer("⌛️ Задача в процессе!")
        return

    await message.answer("Генерация не удалась. Что-то пошло не так! 😔")
