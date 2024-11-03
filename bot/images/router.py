import logging

from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot.filters import TextCommand, StateCommand, StartWithQuery
from bot.gpt.utils import checked_text
from bot.images.command_types import images_command, images_command_text
from bot.utils import divide_into_chunks
from bot.utils import send_photo_as_file
from services import stateService, StateTypes, imageService, tokenizeService
from services.image_utils import image_models_values, samplers_values, \
    steps_values, cgf_values, size_values

imagesRouter = Router()


@imagesRouter.message(StateCommand(StateTypes.Image))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    if not stateService.is_image_state(user_id):
        return

    try:
        wait_message = await message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 15-30 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        imageService.set_waiting_image(user_id, True)

        await message.bot.send_chat_action(message.chat.id, "typing")

        async def wait_image():
            stateService.set_current_state(message.from_user.id, StateTypes.Default)

            await message.answer("Генерация изображения ушла в фоновый режим. \n"
                                 "Пришлем вам изображение через 40-120 секунд. \n"
                                 "Можете продолжать работать с ботом 😉")

        image = await imageService.generate(message.text, user_id, wait_image)

        await message.bot.send_chat_action(message.chat.id, "typing")
        await message.reply_photo(image["output"][0])
        await send_photo_as_file(message, image["output"][0], "Вот картинка в оригинальном качестве")
        await tokenizeService.update_token(user_id, 30, "subtract")
        await message.answer(f"""
🤖 Затрачено на генерацию  30⚡️

❔ /help - Информация по ⚡️
""")
        await wait_message.delete()

    except Exception as e:
        await message.answer("Что-то пошло не так попробуйте позже! 😔")
        logging.log(logging.INFO, e)

    imageService.set_waiting_image(user_id, False)
    stateService.set_current_state(message.from_user.id, StateTypes.Default)


@imagesRouter.message(StateCommand(StateTypes.Flux))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    if not stateService.is_flux_state(user_id):
        return

    stateService.set_current_state(user_id, StateTypes.Default)

    try:
        wait_message = await message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 15-30 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        imageService.set_waiting_image(user_id, True)

        await message.bot.send_chat_action(message.chat.id, "typing")

        async def task_id_get(task_id: str):
            await message.answer(f"""
ID вашей генерации: `1:flux:{task_id}:generate`.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации ⚡️.
""")

        result = await imageService.generate_flux(user_id, message.text, task_id_get)

        image = result['data']["output"]["image_url"]

        await message.bot.send_chat_action(message.chat.id, "typing")
        await message.reply_photo(image)
        await send_photo_as_file(message, image, "Вот картинка в оригинальном качестве")
        await message.answer(text="Cгенерировать Flux еще? 🔥", reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Сгенерировать 🔥",
                        callback_data="flux-generate"
                    )
                ]
            ],
        ))

        model = imageService.get_flux_model(user_id)

        energy = 600

        if model == "Qubico/flux1-dev":
            energy = 2000

        await tokenizeService.update_token(user_id, energy, "subtract")
        await message.answer(f"""
🤖 Затрачено на генерацию {energy}⚡️ 

❔ /help - Информация по ⚡️
""")
        await wait_message.delete()

    except Exception as e:
        await message.answer("Что-то пошло не так попробуйте позже! 😔")
        logging.log(logging.INFO, e)

    imageService.set_waiting_image(user_id, False)
    stateService.set_current_state(message.from_user.id, StateTypes.Default)


@imagesRouter.message(StateCommand(StateTypes.Dalle3))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    tokens = await tokenizeService.get_tokens(message.from_user.id)

    print(tokens)
    if tokens.get("tokens") < 0:
        await message.answer("""
У вас не хватает ⚡️!

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - Пригласить друга, чтобы получить бесплатные ⚡️!       
""")
        stateService.set_current_state(message.from_user.id, StateTypes.Default)
        return

    if not stateService.is_dalle3_state(user_id):
        return

    try:
        wait_message = await message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 15-30 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        imageService.set_waiting_image(user_id, True)

        await message.bot.send_chat_action(message.chat.id, "typing")

        image = await imageService.generate_dalle(user_id, message.text)

        await message.bot.send_chat_action(message.chat.id, "typing")

        await message.answer(image["text"])
        await message.reply_photo(image["image"])
        await send_photo_as_file(message, image["image"], "Вот картинка в оригинальном качестве")
        await message.answer(text="Cгенерировать Dalle3 еще? 🔥", reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Сгенерировать 🔥",
                        callback_data="dalle-generate"
                    )
                ]
            ],
        ))

        await wait_message.delete()

        await tokenizeService.update_token(user_id, image["total_tokens"] * 2, "subtract")
        await message.answer(f"""
🤖 Затрачено на генерацию  *{image["total_tokens"]}*⚡️

❔ /help - Информация по ⚡️
""")
    except Exception as e:
        await message.answer("Что-то пошло не так попробуйте позже! 😔")
        logging.log(logging.INFO, e)

    stateService.set_current_state(message.from_user.id, StateTypes.Default)


async def send_variation_image(message, image, task_id):
    await send_photo_as_file(
        message,
        image,
        "Вот вариации изображения в оригинальном качестве.\n\n"
        "Выберите нужное действие:",
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="U1", callback_data=f'upscale-midjourney {task_id} 1'),
                    InlineKeyboardButton(text="U2", callback_data=f'upscale-midjourney {task_id} 2'),
                    InlineKeyboardButton(text="U3", callback_data=f'upscale-midjourney {task_id} 3'),
                    InlineKeyboardButton(text="U4", callback_data=f'upscale-midjourney {task_id} 4')
                ],
                [
                    InlineKeyboardButton(text="V1", callback_data=f'variation-midjourney {task_id} 1'),
                    InlineKeyboardButton(text="V2", callback_data=f'variation-midjourney {task_id} 2'),
                    InlineKeyboardButton(text="V3", callback_data=f'variation-midjourney {task_id} 3'),
                    InlineKeyboardButton(text="V4", callback_data=f'variation-midjourney {task_id} 4')
                ],
            ],

        )
    )


@imagesRouter.message(StateCommand(StateTypes.Midjourney))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    tokens = await tokenizeService.get_tokens(message.from_user.id)

    if tokens.get("tokens") < 0:
        await message.answer("""
У вас не хватает ⚡️!

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - Пригласить друга, чтобы получить бесплатные ⚡️!       
""")
        stateService.set_current_state(message.from_user.id, StateTypes.Default)
        return

    if not stateService.is_midjourney_state(user_id):
        return

    stateService.set_current_state(message.from_user.id, StateTypes.Default)

    try:
        wait_message = await message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 50-150 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        async def task_id_get(task_id: str):
            await message.answer(f"""
ID вашей генерации: `1:midjourney:{task_id}:generate`.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации ⚡️.
""")

        image = await imageService.generate_midjourney(user_id, message.text, task_id_get)

        await message.bot.send_chat_action(message.chat.id, "typing")

        await send_variation_image(
            message,
            image["task_result"]["discord_image_url"],
            image["task_id"]
        )

        await wait_message.delete()

        await tokenizeService.update_token(user_id, 3300, "subtract")
        await message.answer(f"""
🤖 Затрачено на генерацию 3300⚡️

❔ /help - Информация по ⚡️
""")
    except Exception as e:
        await message.answer("Что-то пошло не так попробуйте позже! 😔")
        logging.log(logging.INFO, e)

    stateService.set_current_state(message.from_user.id, StateTypes.Default)


@imagesRouter.callback_query(StartWithQuery("upscale-midjourney"))
async def upscale_midjourney_callback_query(callback: CallbackQuery):
    task_id = callback.data.split(" ")[1]
    index = callback.data.split(" ")[2]

    wait_message = await callback.message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 15-30 секунд.")

    async def task_id_get(task_id: str):
        await callback.message.answer(f"""
ID вашей генерации: `1:midjourney:{task_id}:upscale`.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации ⚡️.
""")

    image = await imageService.upscale_image(task_id, index, task_id_get)

    await callback.message.reply_photo(image["task_result"]["discord_image_url"])
    await send_photo_as_file(
        callback.message,
        image["task_result"]["discord_image_url"],
        "Вот ваше изображение в оригинальном качестве"
    )
    await callback.message.answer(text="Cгенерировать Midjourney еще?", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Сгенерировать 🔥",
                    callback_data="midjourney-generate"
                )
            ]
        ],
    )
                                  )

    await tokenizeService.update_token(callback.from_user.id, 1000, "subtract")
    await callback.message.answer(f"""
🤖 Затрачено на генерацию 1000⚡️

❔ /help - Информация по ⚡️
""")

    await wait_message.delete()


@imagesRouter.callback_query(StartWithQuery("variation-midjourney"))
async def variation_midjourney_callback_query(callback: CallbackQuery):
    task_id = callback.data.split(" ")[1]
    index = callback.data.split(" ")[2]

    wait_message = await callback.message.answer("**⌛️Ожидайте генерацию...** Примерное время ожидания 50-150 секунд.")

    async def task_id_get(task_id: str):
        await callback.message.answer(f"""
ID вашей генерации: `1:midjourney:{task_id}:generate`.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации ⚡️.
""")

    image = await imageService.variation_image(task_id, index, task_id_get)

    await send_variation_image(
        callback.message,
        image["task_result"]["discord_image_url"],
        image["task_id"]
    )

    await tokenizeService.update_token(callback.from_user.id, 2500, "subtract")
    await callback.message.answer(f"""
🤖 Затрачено на генерацию 2500⚡️

❔ /help - Информация по ⚡️
""")

    await wait_message.delete()


@imagesRouter.message(TextCommand([images_command(), images_command_text()]))
async def handle_start_generate_image(message: types.Message):
    await message.answer(text="🖼️ Выберите модель: ", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                # todo придумать callback data утилиту
                InlineKeyboardButton(text="Stable Duffusion", callback_data="image-model SD"),
                InlineKeyboardButton(text="Dall-e-3", callback_data="image-model Dalle3"),
            ],
            [
                InlineKeyboardButton(text="Midjourney", callback_data="image-model Midjourney"),
                InlineKeyboardButton(text="Flux", callback_data="image-model Flux"),
            ]
        ]))

    await message.bot.send_chat_action(message.chat.id, "typing")


async def generate_base_stable_diffusion_keyboard(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    current_image = imageService.get_current_image(user_id)
    current_size = imageService.get_size_model(user_id)
    current_steps = imageService.get_steps(user_id)
    current_cfg = imageService.get_cfg_model(user_id)

    await callback_query.message.edit_text("Параметры *Stable Diffusion*:")
    await callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"Модель: {current_image}",
                    callback_data="image-model choose-model 0 5"
                )],
                [InlineKeyboardButton(
                    text=f"Размер: {current_size}",
                    callback_data="image-model choose-size 0 5"
                )],
                [
                    InlineKeyboardButton(
                        text=f"Шаги: {current_steps}",
                        callback_data="image-model choose-steps"
                    ),
                    InlineKeyboardButton(
                        text=f"CFG Scale: {current_cfg}",
                        callback_data="image-model choose-cfg"
                    )
                ],
                [InlineKeyboardButton(
                    text=f"Сгенерировать 🔥",
                    callback_data="sd-generate"
                )],
            ],

        )
    )


async def generate_base_midjourney_keyboard(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    current_size = imageService.get_midjourney_size(user_id)

    def size_text(size: str):
        if current_size == size:
            return checked_text(size)
        return size

    await callback_query.message.edit_text("Параметры *Midjourney*:")
    await callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=size_text("1:1"),
                        callback_data="image-model update-size-midjourney 1:1"
                    ),
                    InlineKeyboardButton(
                        text=size_text("2:3"),
                        callback_data="image-model update-size-midjourney 2:3"
                    ),
                    InlineKeyboardButton(
                        text=size_text("4:5"),
                        callback_data="image-model update-size-midjourney 3:2"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=size_text("4:5"),
                        callback_data="image-model update-size-midjourney 4:5"
                    ),
                    InlineKeyboardButton(
                        text=size_text("5:4"),
                        callback_data="image-model update-size-midjourney 5:4"
                    ),
                    InlineKeyboardButton(
                        text=size_text("4:7"),
                        callback_data="image-model update-size-midjourney 4:7"
                    ),
                    InlineKeyboardButton(
                        text=size_text("7:4"),
                        callback_data="image-model update-size-midjourney 7:4"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"Сгенерировать 🔥",
                        callback_data="midjourney-generate"
                    )
                ],
            ],

        )
    )


async def generate_base_dalle3_keyboard(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    current_size = imageService.get_dalle_size(user_id)

    def size_text(size: str):
        if current_size == size:
            return checked_text(size)
        return size

    await callback_query.message.edit_text("Параметры *Dall-e-3*:")
    await callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=size_text("1024x1024"),
                    callback_data="image-model update-size-dalle 1024x1024"
                )],
                [InlineKeyboardButton(
                    text=size_text("1024x1792"),
                    callback_data="image-model update-size-dalle 1024x1792"
                )],
                [InlineKeyboardButton(
                    text=size_text("1792x1024"),
                    callback_data="image-model update-size-dalle 1792x1024"
                )],
                [InlineKeyboardButton(
                    text=f"Сгенерировать 🔥",
                    callback_data="dalle-generate"
                )],
            ],

        )
    )


async def generate_base_flux_keyboard(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    current_model = imageService.get_flux_model(user_id)

    def model_text(model: str, text):
        if current_model == model:
            return checked_text(text)
        return text

    await callback_query.message.edit_text("Параметры *Flux*:")
    await callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=model_text("Qubico/flux1-dev", "Модель: Flux-Dev"),
                    callback_data="image-model update-flux-model Qubico/flux1-dev"
                )],
                [InlineKeyboardButton(
                    text=model_text("Qubico/flux1-schnell", "Модель: Flux-Schnell"),
                    callback_data="image-model update-flux-model Qubico/flux1-schnell"
                )],
                [InlineKeyboardButton(
                    text=f"Сгенерировать 🔥",
                    callback_data="flux-generate"
                )],
            ],

        )
    )


def normalize_start_index(index_start: int):
    return index_start if index_start > 0 else 0


def normalize_end_index(index_end: int, max_index: int):
    return index_end if index_end < max_index else max_index


@imagesRouter.callback_query(StartWithQuery("sd-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Image)
    await callback_query.message.answer("""
Напишите запрос на английком языке для генерации изображения! ‍🔥

Например: `an astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed`
""")


@imagesRouter.callback_query(StartWithQuery("flux-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Flux)
    await callback_query.message.answer("""
Напишите запрос на английком языке для генерации изображения! ‍🔥

Например: `an astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed`
""")


@imagesRouter.callback_query(StartWithQuery("dalle-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Dalle3)
    await callback_query.message.answer("""
Напишите запрос для генерации изображения! ‍🔥

Например: `Нарисуй черную дыру, которая поглощает галактики`
""")


@imagesRouter.callback_query(StartWithQuery("midjourney-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Midjourney)
    await callback_query.message.answer(""" 
Напишите на английском запрос для генерации изображения! ‍🔥

Например: `A fantastic photorealistic photo of a black hole that destroys other galaxies`
""")


@imagesRouter.callback_query(StartWithQuery("image-model"))
async def handle_image_model_query(callback_query: CallbackQuery):
    model = callback_query.data.split(" ")[1]

    user_id = callback_query.from_user.id

    if model == "SD":
        await generate_base_stable_diffusion_keyboard(callback_query)

    if model == "Dalle3":
        await generate_base_dalle3_keyboard(callback_query)

    if model == "Midjourney":
        await generate_base_midjourney_keyboard(callback_query)

    if model == "Flux":
        await generate_base_flux_keyboard(callback_query)

    if model == "update-flux-model":
        value = callback_query.data.split(" ")[2]

        imageService.set_flux_model(user_id, value)

        await generate_base_flux_keyboard(callback_query)

    if model == "update-size-midjourney":
        size = callback_query.data.split(" ")[2]

        imageService.set_midjourney_size(user_id, size)

        await generate_base_midjourney_keyboard(callback_query)

    if model == "update-size-dalle":
        dalle_size = callback_query.data.split(" ")[2]

        imageService.set_dalle_size(user_id, dalle_size)

        await generate_base_dalle3_keyboard(callback_query)

    if model == "update-model":
        model = callback_query.data.split(" ")[2]

        imageService.set_current_image(user_id, model)

        await generate_base_stable_diffusion_keyboard(callback_query)

    if model == "update-sampler":
        model = callback_query.data.split(" ")[2]
        print(model)

        imageService.set_sampler_state(user_id, model)

        await generate_base_stable_diffusion_keyboard(callback_query)

    if model == "choose-model":
        index_start_data = int(callback_query.data.split(" ")[2])
        index_end_data = int(callback_query.data.split(" ")[3])

        stable_models = list(
            map(lambda x: [InlineKeyboardButton(text=x, callback_data=f"image-model update-model {x}")],
                image_models_values))

        index_start = normalize_start_index(index_start_data)
        index_end = normalize_end_index(index_end_data, len(stable_models))

        copy_stable_models = stable_models[index_start:index_end]

        copy_stable_models.append([InlineKeyboardButton(text="❌ Отменить",
                                                        callback_data=f"image-model SD")])

        if index_start != 0:
            copy_stable_models.append([InlineKeyboardButton(text="⬅️ Назад",
                                                            callback_data=f"image-model choose-model {normalize_start_index(index_start - 5)} {index_start}")])

        if index_end != len(stable_models):
            copy_stable_models.append([InlineKeyboardButton(text="➡️ Вперед",
                                                            callback_data=f"image-model choose-model {index_start + 5} {normalize_end_index(index_end + 5, len(stable_models))}")])

        start_page = int(index_start / 5) + 1
        end_page = int(len(stable_models) / 5) + 1

        await callback_query.message.edit_text(f"""
📄 Страница *{start_page}* из *{end_page}*
👾 Модели Stable Diffusion: 
        
        """)
        await callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=copy_stable_models
            )
        )

    if model == "update-size":
        size = callback_query.data.split(" ")[2]

        imageService.set_size_state(user_id, size)

        await generate_base_stable_diffusion_keyboard(callback_query)

    if model == "choose-size":
        keyboard = divide_into_chunks(
            list(
                map(lambda x: InlineKeyboardButton(text=str(x), callback_data=f"image-model update-size {x}"),
                    size_values)),
            2
        )

        keyboard.append([InlineKeyboardButton(text="❌ Отменить",
                                              callback_data=f"image-model SD")])

        await callback_query.message.edit_text("👾 Шаги Stable Diffusion: ")
        await callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=keyboard
            )
        )

    if model == "choose-sampler":
        index_start_data = int(callback_query.data.split(" ")[2])
        index_end_data = int(callback_query.data.split(" ")[3])

        stable_models = list(
            map(lambda x: [InlineKeyboardButton(text=x, callback_data=f"image-model update-sampler {x}")],
                samplers_values))

        index_start = normalize_start_index(index_start_data)
        index_end = normalize_end_index(index_end_data, len(stable_models))

        copy_stable_models = stable_models[index_start:index_end]

        copy_stable_models.append([InlineKeyboardButton(text="❌ Отменить",
                                                        callback_data=f"image-model SD")])

        start_page = int(index_start / 5) + 1
        end_page = int(len(stable_models) / 5) + 1

        if index_start != 0:
            copy_stable_models.append([InlineKeyboardButton(text="⬅️ Назад",
                                                            callback_data=f"image-model choose-sampler {normalize_start_index(index_start - 5)} {index_start}")])

        if index_end != len(stable_models):
            copy_stable_models.append([InlineKeyboardButton(text="➡️ Вперед",
                                                            callback_data=f"image-model choose-sampler {index_start + 5} {normalize_end_index(index_end + 5, len(stable_models))}")])

        await callback_query.message.edit_text(f"""
    📄 Страница *{start_page}* из *{end_page}*
    👾 Сэмплеры Stable Diffusion: 

            """)
        await callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=copy_stable_models
            )
        )

    if model == "update-step":
        model = callback_query.data.split(" ")[2]

        imageService.set_steps_state(user_id, model)

        await generate_base_stable_diffusion_keyboard(callback_query)

    if model == "choose-steps":
        keyboard = divide_into_chunks(
            list(
                map(lambda x: InlineKeyboardButton(text=str(x), callback_data=f"image-model update-step {x}"),
                    steps_values)),
            4
        )

        keyboard.append([InlineKeyboardButton(text="❌ Отменить",
                                              callback_data=f"image-model SD")])

        await callback_query.message.edit_text("👾 Шаги Stable Diffusion: ")
        await callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=keyboard
            )
        )

    if model == "update-cfg":
        model = callback_query.data.split(" ")[2]

        imageService.set_cfg_state(user_id, model)

        await generate_base_stable_diffusion_keyboard(callback_query)

    if model == "choose-cfg":
        keyboard = divide_into_chunks(
            list(
                map(lambda x: InlineKeyboardButton(text=str(x), callback_data=f"image-model update-cfg {x}"),
                    cgf_values)),
            4
        )

        keyboard.append([InlineKeyboardButton(text="❌ Отменить",
                                              callback_data=f"image-model SD")])

        await callback_query.message.edit_text("👾 CFG Scale Stable Diffusion: ")
        await callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=keyboard
            )
        )
