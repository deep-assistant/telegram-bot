import logging

from aiogram import Router, types

from bot.filters import TextCommand, StateCommand
from bot.images.command_types import images_command, images_command_text
from services import stateService, StateTypes, imageService

imagesRouter = Router()


@imagesRouter.message(StateCommand(StateTypes.Image))
async def handle_generate_image(message: types.Message):
    if not stateService.is_image_state(message.from_user.id):
        return

    try:
        wait_message = await message.answer("**⌛️Ожидайте генерацию...**")

        await message.bot.send_chat_action(message.chat.id, "typing")

        image = imageService.generate(message.text)
        await message.reply_photo(image["output"][0])
        await wait_message.delete()
    except Exception as e:
        await message.reply_photo("Что-то пошло не так попробуйте позже! 😔")
        logging.log(logging.INFO, e)

    stateService.set_current_state(message.from_user.id, StateTypes.Default)


@imagesRouter.message(TextCommand([images_command(), images_command_text()]))
async def handle_start_generate_image(message: types.Message):
    stateService.set_current_state(message.from_user.id, StateTypes.Image)

    await message.answer("Напишите запрос на английком языке для генерации изображения! ‍🔥")
    await message.bot.send_chat_action(message.chat.id, "typing")
