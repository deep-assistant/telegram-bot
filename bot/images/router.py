import logging
import re

from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot.filters import TextCommand, StateCommand, StartWithQuery
from bot.gpt.utils import checked_text
from bot.commands import images_command, images_command_text
from bot.main_keyboard import create_main_keyboard
from bot.utils import divide_into_chunks
from bot.utils import send_photo_as_file, send_photo
from bot.constants import DEFAULT_ERROR_MESSAGE
from bot.empty_prompt import is_empty_prompt
from services import stateService, StateTypes, imageService, tokenizeService
from services.image_utils import image_models_values, samplers_values, \
    steps_values, cgf_values, size_values

imagesRouter = Router()

# Confirmed banned words from error data
confirmed_banned_words = [
    "blood",
    "chest",
    "cutting",
    "dick",
    "flesh",
    "miniskirt",
    "naked",
    "nude",
    "provocative",
    "sex",
    "sexy",
    "shirtless",
    "shit",
    "succubus",
    "trump"
]

# Unconfirmed banned words from provided sources, categorized
unconfirmed_banned_words = {
    "gore_words": [
        "blood", "bloodbath", "crucifixion", "bloody", "flesh", "bruises", "car crash", "corpse",
        "crucified", "cutting", "decapitate", "infested", "gruesome", "kill", "infected", "sadist",
        "slaughter", "teratoma", "tryphophobia", "wound", "cronenberg", "khorne", "cannibal",
        "cannibalism", "visceral", "guts", "bloodshot", "gory", "killing", "surgery", "vivisection",
        "massacre", "hemoglobin", "suicide"
    ],
    "adult_words": [
        "ahegao", "pinup", "ballgag", "playboy", "bimbo", "pleasure", "bodily fluids", "pleasures",
        "boudoir", "rule34", "brothel", "seducing", "dominatrix", "seductive", "erotic seductive",
        "fuck", "sensual", "hardcore", "sexy", "hentai", "shag", "horny", "shibari", "incest",
        "smut", "jav", "succubus", "jerk off king at pic", "thot", "kinbaku", "transparent",
        "submissive", "dominant", "nasty", "indecent", "legs spread", "cussing", "flashy", "twerk",
        "making love", "voluptuous", "naughty", "wincest", "orgy", "sultry", "xxx", "bondage",
        "bdsm", "dog collar", "slavegirl", "transparent and translucent"
    ],
    "body_parts_words": [
        "arse", "labia", "ass", "mammaries", "human centipede", "badonkers", "minge", "massive chests",
        "big ass", "mommy milker", "booba", "nipple", "booty", "oppai", "bosom", "melons", "bulging",
        "coochie", "head", "engorged", "organs", "breasts", "ovaries", "busty", "penis", "clunge",
        "phallus", "crotch", "sexy female", "dick", "skimpy", "girth", "thick", "honkers", "vagina",
        "hooters", "veiny", "knob", "seductress", "shaft"
    ],
    "nudity_words": [
        "no clothes", "speedo", "au naturale", "no shirt", "bare chest", "nude", "barely dressed",
        "bra", "risqué", "clear", "scantily", "clad", "cleavage", "stripped", "full frontal unclothed",
        "invisible clothes", "wearing nothing", "lingerie with no shirt", "naked", "without clothes on",
        "negligee", "zero clothes"
    ],
    "taboo_words": [
        "taboo", "fascist", "nazi", "prophet mohammed", "slave", "coon", "honkey", "arrested", "jail",
        "handcuffs", "torture", "disturbing", "1488"
    ],
    "drugs_words": [
        "drugs", "cocaine", "heroin", "meth", "crack"
    ],
    "other_words": [
        "farts", "fart", "poop", "warts", "xi jinping", "shit", "pleasure", "errect", "big black",
        "brown pudding", "bunghole", "vomit", "voluptuous", "seductive", "sperm", "hot", "sexy",
        "plebeian", "sensored", "censored", "uncouth", "silenced", "deepfake", "inappropriate",
        "pus", "waifu", "mp5", "succubus", "surgery"
    ]
}

# Create a single set of all banned words for efficient lookup
banned_words_set = set(confirmed_banned_words)
for category_words in unconfirmed_banned_words.values():
    banned_words_set.update(category_words)

def is_banned_word(word):
    """Check if a word or phrase is in the banned words set.

    Args:
        word (str): The word or phrase to check.

    Returns:
        bool: True if the word is banned, False otherwise.
    """
    return word.lower() in banned_words_set

def get_banned_words(text):
    words = text.split(" ")
    words = [word.lower() for word in words]
    banned_words_in_request = [word for word in words if is_banned_word(word)]
    return banned_words_in_request

# # Example usage
# if __name__ == "__main__":
#     test_words = ["blood", "sexy", "dog", "naked", "torture", "hello", "succubus"]
#     for test_word in test_words:
#         if is_banned_word(test_word):
#             print(f"'{test_word}' is banned")
#         else:
#             print(f"'{test_word}' is not banned")

@imagesRouter.message(StateCommand(StateTypes.Image))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    try:
        if not stateService.is_image_state(user_id):
            return
        
        tokens = await tokenizeService.get_tokens(user_id)
        if tokens.get("tokens") < 0:
            await message.answer("""
У вас не хватает *⚡️*. 😔

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!       
""")
            stateService.set_current_state(user_id, StateTypes.Default)
            return
        
        if (is_empty_prompt(message.text)):
            await message.answer(
                "🚫 В вашем запросе отсутствует описание изображения 🖼️. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-sd-generate"
                            )
                        ]
                    ],
                )
            )
            return

        stateService.set_current_state(user_id, StateTypes.Default)

        wait_message = await message.answer("**⌛️Ожидайте генерацию...**\nПримерное время ожидания 15-30 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        imageService.set_waiting_image(user_id, True)

        await message.bot.send_chat_action(message.chat.id, "typing")

        async def wait_image():
            await message.answer("Генерация изображения ушла в фоновый режим. \n"
                                 "Пришлем вам изображение через 40-120 секунд. \n"
                                 "Можете продолжать работать с ботом 😉")

        image = await imageService.generate(message.text, user_id, wait_image)

        await message.bot.send_chat_action(message.chat.id, "typing")
        await message.reply_photo(image["output"][0])
        await send_photo_as_file(message, image["output"][0], "Вот картинка в оригинальном качестве")
        await tokenizeService.update_token(user_id, 30, "subtract")
        await message.answer(f"""
🤖 Затрачено на генерацию изображения Stable Diffusion 30⚡️

❔ /help - Информация по ⚡️
""")
        await wait_message.delete()

    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to generate image: {e}")

    imageService.set_waiting_image(user_id, False)
    stateService.set_current_state(user_id, StateTypes.Default)


@imagesRouter.message(StateCommand(StateTypes.Flux))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    try:
        if not stateService.is_flux_state(user_id):
            return
        
        tokens = await tokenizeService.get_tokens(user_id)
        if tokens.get("tokens") < 0:
            await message.answer("""
У вас не хватает *⚡️*. 😔
                                 
/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!
""")
            stateService.set_current_state(user_id, StateTypes.Default)
            return
        
        if (is_empty_prompt(message.text)):
            await message.answer(
                "🚫 В вашем запросе отсутствует описание изображения 🖼️. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-flux-generate"
                            )
                        ]
                    ],
                )
            )
            return

        stateService.set_current_state(user_id, StateTypes.Default)

        wait_message = await message.answer("**⌛️Ожидайте генерацию...**\nПримерное время ожидания 15-30 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        imageService.set_waiting_image(user_id, True)

        await message.bot.send_chat_action(message.chat.id, "typing")

        async def task_id_get(task_id: str):
            await message.answer(f"`1:flux:{task_id}:generate`")
            await message.answer(f"""Это ID вашей генерации.

Просто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.
                                 
Вы также получите результат генерации по готовности.
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
🤖 Затрачено на генерацию изображения Flux {energy}⚡️ 

❔ /help - Информация по ⚡️
""")
        await wait_message.delete()

    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to generate Flux image: {e}")

    imageService.set_waiting_image(user_id, False)
    stateService.set_current_state(message.from_user.id, StateTypes.Default)


@imagesRouter.message(StateCommand(StateTypes.Dalle3))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    try:
        if not stateService.is_dalle3_state(user_id):
            return

        tokens = await tokenizeService.get_tokens(user_id)
        if tokens.get("tokens") < 0:
            await message.answer("""
У вас не хватает *⚡️*. 😔

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!       
""")
            stateService.set_current_state(user_id, StateTypes.Default)
            return
        
        if (is_empty_prompt(message.text)):
            await message.answer(
                "🚫 В вашем запросе отсутствует описание изображения 🖼️. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-dalle-generate"
                            )
                        ]
                    ],
                )
            )
            return

        stateService.set_current_state(user_id, StateTypes.Default)

        wait_message = await message.answer("**⌛️Ожидайте генерацию...**\nПримерное время ожидания 15-30 секунд.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        imageService.set_waiting_image(user_id, True)

        await message.bot.send_chat_action(message.chat.id, "typing")

        image = await imageService.generate_dalle(user_id, message.text)

        await message.bot.send_chat_action(message.chat.id, "typing")

        await message.answer(image["text"])
        await message.reply_photo(image["image"])
        await send_photo_as_file(message, image["image"], "Вот картинка в оригинальном качестве")
        await message.answer(text="Cгенерировать DALL·E 3 еще? 🔥", reply_markup=InlineKeyboardMarkup(
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
🤖 Затрачено на генерацию изображения DALL·E 3 *{image["total_tokens"] * 2}*⚡️

❔ /help - Информация по ⚡️
""")
    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to generate DALL·E 3 image: {e}")
        stateService.set_current_state(user_id, StateTypes.Default)


async def send_variation_image(message, image, task_id):
    await send_photo(
        message,
        image,
        """Номера вариаций:
```
+-------+-------+
|   1   |   2   |
+-------+-------+
|   3   |   4   |
+-------+-------+
```

Доступные действия:
U - Увеличить изображение (Upscale)
V - Сгенерировать вариации выбранного изображения (Variation)

Каждое действие можно выполнить над картинкой с соответствующим номером.

Выберите нужное действие:
""",
        ext=".png",
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="U1", callback_data=f'upscale-midjourney {task_id} 1'),
                    InlineKeyboardButton(text="U2", callback_data=f'upscale-midjourney {task_id} 2'),
                    InlineKeyboardButton(text="V1", callback_data=f'variation-midjourney {task_id} 1'),
                    InlineKeyboardButton(text="V2", callback_data=f'variation-midjourney {task_id} 2'),
                ],
                [
                    InlineKeyboardButton(text="U3", callback_data=f'upscale-midjourney {task_id} 3'),
                    InlineKeyboardButton(text="U4", callback_data=f'upscale-midjourney {task_id} 4'),
                    InlineKeyboardButton(text="V3", callback_data=f'variation-midjourney {task_id} 3'),
                    InlineKeyboardButton(text="V4", callback_data=f'variation-midjourney {task_id} 4'),
                ],
            ],

        )
    )


@imagesRouter.message(StateCommand(StateTypes.Midjourney))
async def handle_generate_image(message: types.Message):
    user_id = message.from_user.id

    main_keyboard = create_main_keyboard()

    try:
        if not stateService.is_midjourney_state(user_id):
            return

        tokens = await tokenizeService.get_tokens(user_id)
        if tokens.get("tokens") < 0:
            await message.answer("""
У вас не хватает *⚡️*. 😔

/balance - ✨ Проверить Баланс
/buy - 💎 Пополнить баланс
/referral - 👥 Пригласить друга, чтобы получить больше *⚡️*!       
""", reply_markup=main_keyboard)
            stateService.set_current_state(user_id, StateTypes.Default)
            return

        if (is_empty_prompt(message.text)):
            await message.answer(
                "🚫 В вашем запросе отсутствует описание изображения 🖼️. Пожалуйста, попробуйте снова.",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-midjourney-generate"
                            )
                        ]
                    ],
                )
            )
            return

        # Check for prompts starting with "/" which are not accepted by Midjourney
        if message.text.strip().startswith('/'):
            await message.answer(
                """🚫 Запросы, начинающиеся с "/", не принимаются Midjourney.

Пожалуйста, опишите что вы хотите создать без использования команд. Например: "Сибирский кот ест суп" вместо "/image сибирский кот ест суп".""",
                reply_markup=InlineKeyboardMarkup(
                    resize_keyboard=True,
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Отмена ❌",
                                callback_data="cancel-midjourney-generate"
                            )
                        ]
                    ],
                )
            )
            return

        banned_words_in_request = get_banned_words(message.text)
        if banned_words_in_request:
            await message.answer(
                f"""🚫 В вашем запросе обнаружены запрещенные слова: "{'", "'.join(banned_words_in_request)}".

Пожалуйста, попробуйте изменить запрос и отправить его снова.
Если вы считаете, что любое из слов было запрещено по ошибке, пожалуйста, напишите нам в раздел *Ошибки* в сообщество @deepGPT.""",            
                reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отмена ❌",
                            callback_data="cancel-midjourney-generate"
                        )
                    ]
                ],
            ))
            return
        
        stateService.set_current_state(message.from_user.id, StateTypes.Default)

        wait_message = await message.answer("**⌛️Ожидайте генерацию...**\nПримерное время ожидания *1-3 минуты*.", reply_markup=main_keyboard)

        await message.bot.send_chat_action(message.chat.id, "typing")

        async def task_id_get(task_id: str):
            await message.answer(f"`1:midjourney:{task_id}:generate`")
            await message.answer(f"""Это ID вашей генерации.
                                 
Просто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.
                                 
Вы также получите результат генерации по готовности.""")

        image = await imageService.generate_midjourney(user_id, message.text, task_id_get)

        await message.bot.send_chat_action(message.chat.id, "typing")

        await send_variation_image(
            message,
            image["task_result"]["discord_image_url"],
            image["task_id"]
        )

        await wait_message.delete()

        await tokenizeService.update_token(user_id, 4200, "subtract")
        await message.answer(f"""
🤖 Затрачено на генерацию изображений Midjourney 4200⚡️

❔ /help - Информация по ⚡️
""")
    except Exception as e:
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.error(f"Failed to generate Midjourney image: {e}")
        stateService.set_current_state(message.from_user.id, StateTypes.Default)


@imagesRouter.callback_query(StartWithQuery("upscale-midjourney"))
async def upscale_midjourney_callback_query(callback: CallbackQuery):
    task_id = callback.data.split(" ")[1]
    index = callback.data.split(" ")[2]

    wait_message = await callback.message.answer("**⌛️Ожидайте генерацию...**\nПримерное время ожидания *1-3 минуты*.")

    async def task_id_get(task_id: str):
        await callback.message.answer(f"`1:midjourney:{task_id}:upscale`")
        await callback.message.answer(f"""Это ID вашей генерации.
                                      
Просто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.
                                      
Вы также получите результат генерации по готовности.""")

    image = await imageService.upscale_image(task_id, index, task_id_get)

    await callback.message.reply_photo(image["task_result"]["discord_image_url"])
    await send_photo_as_file(
        callback.message,
        image["task_result"]["discord_image_url"],
        ext=".png",
        caption="Вот ваше изображение в оригинальном качестве"
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

    await tokenizeService.update_token(callback.from_user.id, 1600, "subtract")
    await callback.message.answer(f"""
🤖 Затрачено на генерацию увеличенного изображения Midjourney 1600⚡️

❔ /help - Информация по ⚡️
""")

    await wait_message.delete()


@imagesRouter.callback_query(StartWithQuery("variation-midjourney"))
async def variation_midjourney_callback_query(callback: CallbackQuery):
    task_id = callback.data.split(" ")[1]
    index = callback.data.split(" ")[2]

    wait_message = await callback.message.answer("**⌛️Ожидайте генерацию...**\nПримерное время ожидания *1-3 минуты*.")

    async def task_id_get(task_id: str):
        await callback.message.answer(f"`1:midjourney:{task_id}:generate`")
        await callback.message.answer(f"""Это ID вашей генерации.
                                      
Просто отправьте этот ID в чат и получите актуальный статус вашей генерации в любой удобный для вас момент.
                                      
Вы также получите результат генерации по готовности.""")

    image = await imageService.variation_image(task_id, index, task_id_get)

    await send_variation_image(
        callback.message,
        image["task_result"]["discord_image_url"],
        image["task_id"]
    )

    await tokenizeService.update_token(callback.from_user.id, 8700, "subtract")
    await callback.message.answer(f"""
🤖 Затрачено на генерацию вариации изображения Midjourney 8700⚡️

❔ /help - Информация по ⚡️
""")

    await wait_message.delete()

# Черновик прайс листа для Midjourney (для остальных моделей нужно проводить исследование, чтобы составить хотя бы приблизительный прайс-лист)
#   - Первичная генерация - 3300⚡️
#   - Генерация вариаций - 2500⚡️
#   - Увеличение изображения - 1000⚡️

@imagesRouter.message(TextCommand([images_command(), images_command_text()]))
async def handle_start_generate_image(message: types.Message):
    await message.answer(text="""🖼️ Выберите модель:

⦁ [Midjourney](https://en.wikipedia.org/wiki/Midjourney)
⦁ [DALL·E 3](https://en.wikipedia.org/wiki/DALL-E)
⦁ [Flux](https://en.wikipedia.org/wiki/FLUX.1)
⦁ [Stable Diffusion](https://en.wikipedia.org/wiki/Stable_Diffusion)
""", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Midjourney", callback_data="image-model Midjourney"),
                InlineKeyboardButton(text="DALL·E 3", callback_data="image-model Dalle3"),
            ],
            [
                # todo придумать callback data утилиту
                InlineKeyboardButton(text="Flux", callback_data="image-model Flux"),
                InlineKeyboardButton(text="Stable Duffusion", callback_data="image-model SD"),
            ]
        ]),
        link_preview_options={"is_disabled": True})

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

generate_button_name = 'Cгенерировать'

async def generate_base_midjourney_keyboard(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    current_size = imageService.get_midjourney_size(user_id)

    def size_text(size: str):
        if current_size == size:
            return checked_text(size)
        return size

    await callback_query.message.edit_text(f"""Параметры *Midjourney*:

Выберите соотношение сторон изображения. Текущее соотношение отмечено галочкой.

После этого нажмите кнопку `{generate_button_name}`.
""")
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
                        text=size_text("3:2"),
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
                        text=f"{generate_button_name} 🔥",
                        callback_data="midjourney-generate"
                    ),
                    InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="cancel-midjourney-generate"
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
Напишите запрос для генерации изображения! ‍🖼️

Например: `an astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed`
""", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отмена ❌",
                    callback_data="cancel-sd-generate"
                )
            ]
        ],
    ))
    
@imagesRouter.callback_query(StartWithQuery("cancel-sd-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Default)
    await callback_query.message.delete()
    await callback_query.answer("Режим генерации изображения в Stable Diffusion успешно отменён!")


@imagesRouter.callback_query(StartWithQuery("flux-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Flux)
    await callback_query.message.answer("""
Напишите запрос для генерации изображения! ‍🖼️

Например: `an astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed`
""", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отмена ❌",
                    callback_data="cancel-flux-generate"
                )
            ]
        ],
    ))
    
@imagesRouter.callback_query(StartWithQuery("cancel-flux-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Default)
    await callback_query.message.delete()
    await callback_query.answer("Режим генерации изображения в Flux успешно отменён!")


@imagesRouter.callback_query(StartWithQuery("dalle-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Dalle3)
    await callback_query.message.answer("""
Напишите запрос для генерации изображения! ‍🖼️

Например: `Нарисуй черную дыру, которая поглощает галактики`
""", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отмена ❌",
                    callback_data="cancel-dalle-generate"
                )
            ]
        ],
    ))

@imagesRouter.callback_query(StartWithQuery("cancel-dalle-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Default)
    await callback_query.message.delete()
    await callback_query.answer("Режим генерации изображения в DALL·E 3 отменен.")


@imagesRouter.callback_query(StartWithQuery("midjourney-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Midjourney)
    await callback_query.message.delete()
    await callback_query.message.answer("""
Выберите один из вариантов запроса для генерации изображения 🖼️ в меню снизу.
""", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            # [KeyboardButton(text="Фотореалистичная чёрная дыра в космосе, поглощающая галактики.")],
            [KeyboardButton(text="Photorealistic black hole in space, absorbing galaxies.")],
            # [KeyboardButton(text="City skyline at night, futuristic, neon lights, high detail.")],
            [KeyboardButton(text="Силуэт города ночью, футуристический, неоновые огни, высокая детализация.")],
            [KeyboardButton(text="An astronaut riding a horse on mars artstation, hd, dramatic lighting, detailed.")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))

    await callback_query.message.answer(""" 
Или напишите свой запрос для генерации изображения на любом языке, выбор языка может менять стилистические особенности изображений.

Например: "город" на русском языке может выглядеть как город из России, а "city" на английском языке как город из США или из другой страны.
""", reply_markup=InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отмена ❌",
                    callback_data="cancel-midjourney-generate"
                )
            ]
        ],
    ))

@imagesRouter.callback_query(StartWithQuery("cancel-midjourney-generate"))
async def handle_image_model_query(callback_query: CallbackQuery):
    stateService.set_current_state(callback_query.from_user.id, StateTypes.Default)
    await callback_query.message.delete()
    main_keyboard = create_main_keyboard()
    await callback_query.message.answer("Режим генерации изображения в Midjourney успешно отменён!", reply_markup=main_keyboard)

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
