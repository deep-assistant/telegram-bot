import logging

from aiogram import Router, types

from bot.filters import TextCommand, StateCommand
from bot.images.command_types import images_command, images_command_text
from services import stateService, StateTypes, imageService

imagesRouter = Router()


@imagesRouter.message(StateCommand(StateTypes.Image))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    if not stateService.is_image_state(user_id):
        return

    is_waiting_image = imageService.get_waiting_image(user_id)

    if is_waiting_image:
        return

    try:
        wait_message = await message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 15-30 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        imageService.set_waiting_image(user_id, True)

        image = await imageService.generate(message.text)
        await message.reply_photo(image["output"][0])
        await wait_message.delete()
    except Exception as e:
        await message.answer("Что-то пошло не так попробуйте позже! 😔")
        logging.log(logging.INFO, e)

    imageService.set_waiting_image(user_id, False)
    stateService.set_current_state(message.from_user.id, StateTypes.Default)


@imagesRouter.message(TextCommand([images_command(), images_command_text()]))
async def handle_start_generate_image(message: types.Message):
    stateService.set_current_state(message.from_user.id, StateTypes.Image)

    await message.answer("Напишите запрос на английком языке для генерации изображения! ‍🔥")
    await message.bot.send_chat_action(message.chat.id, "typing")
