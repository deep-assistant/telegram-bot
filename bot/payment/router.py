import asyncio
import logging

from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.filters import TextCommand, StartWithQuery
from bot.payment.command_types import payment_command_start, payment_command_text, balance_payment_command_text, \
    balance_payment_command_start
from bot.payment.products import donation_product, buy_balance_product
from services import GPTModels, tokenizeService

paymentsRouter = Router()

donation_text = """
Благодарим за поддержку проекта! 🤩    
Скоро мы будем радовать вас новым и крутым функционалом!

Выбери сумму пожертвования:
"""

# Создание кнопок для выбора суммы пожертвования
donation_buttons = [
    [
        InlineKeyboardButton(text="10 RUB", callback_data="donation 10"),
        InlineKeyboardButton(text="50 RUB", callback_data="donation 50"),
        InlineKeyboardButton(text="100 RUB", callback_data="donation 100"),
    ],
    [
        InlineKeyboardButton(text="150 RUB", callback_data="donation 150"),
        InlineKeyboardButton(text="250 RUB", callback_data="donation 250"),
        InlineKeyboardButton(text="500 RUB", callback_data="donation 500"),
    ]
]


def payment_keyboard(stars):  
    builder = InlineKeyboardBuilder()  
    builder.button(text=f"Оплатить {stars} ⭐️", pay=True)  
  
    return builder.as_markup()


# Создание клавиатуры для выбора модели
def create_buy_balance_keyboard_model():
    return InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🤖 GPT-4o", callback_data=f"buy-gpt {GPTModels.GPT_4o.value}"),
                InlineKeyboardButton(text="🦾 GPT-3.5", callback_data=f"buy-gpt {GPTModels.GPT_3_5.value}"),
            ],
        ])

# Создание клавиатуры для выбора способа оплаты
def create_buy_balance_keyboard_paym_payment(model):
    return InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Telegram Stars", callback_data=f"buy_method_stars {model} stars"),
                # InlineKeyboardButton(text="Опалата картой", callback_data=f"buy_method_card {model} card"),
            ],
        ]
    )

# Обработчик команды /buy
@paymentsRouter.message(TextCommand([payment_command_start(), payment_command_text()]))
async def buy(message: types.Message):
    await message.answer(
        text=donation_text,
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=donation_buttons
        )
    )

# Обработчик команды /balance
@paymentsRouter.message(TextCommand([balance_payment_command_text(), balance_payment_command_start()]))
async def buy_balance(message: types.Message):
    await message.answer(text="Баланс какой модели вы хотите пополнить?", reply_markup=create_buy_balance_keyboard_model())

# Обработчик запроса "назад к выбору модели"
@paymentsRouter.callback_query(StartWithQuery("back_buy_model"))
async def handle_buy_balance_query(callback_query: CallbackQuery):
    try:
        await callback_query.message.edit_text(text="Баланс какой модели вы хотите пополнить?")
        await callback_query.message.edit_reply_markup(reply_markup=create_buy_balance_keyboard_model())
    except Exception:
        pass

# Обработчик запроса выбора модели
@paymentsRouter.callback_query(StartWithQuery("buy-gpt"))
async def handle_buy_balance_model_query(callback_query: CallbackQuery):
    model = callback_query.data.split(" ")[1]
    await callback_query.message.edit_text(text="Выбирете способ оплаты")
    await callback_query.message.edit_reply_markup(reply_markup=create_buy_balance_keyboard_paym_payment(model))

# Обработчик запроса "назад к выбору способа оплаты"
@paymentsRouter.callback_query(StartWithQuery("back_buy_method"))
async def handle_buy_balance_query(callback_query: CallbackQuery):
    model = callback_query.data.split(" ")[1]
    try:
        await callback_query.message.edit_text(text="Выбирете способ оплаты")
        await callback_query.message.edit_reply_markup(reply_markup=create_buy_balance_keyboard_paym_payment(model))
    except Exception:
        pass

# Обработчик запроса покупки токенов Telegram Stars
@paymentsRouter.callback_query(StartWithQuery("buy_method_stars"))
async def handle_buy_balance_model_query(callback_query: CallbackQuery):
    model = callback_query.data.split(" ")[1]
    await callback_query.message.edit_text("""
На сколько токенов вы хотите пополнить баланс?

На данный момент действует скидка! 
Успей получить токены в 2-4 раза дешевле!
""")

    if GPTModels.GPT_3_5.value == model:
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="25,000 токенов (1̶̶̶5̶̶̶  10 ⭐️)",
                                         callback_data=f"buy_stars 25,000 10 {model}"),
                ],
                [
                    InlineKeyboardButton(text="50,000 токенов (4̶5̶  25 ⭐️)",
                                         callback_data=f"buy_stars 50,000 25 {model}"),
                ],
                [
                    InlineKeyboardButton(text="100,000 токенов (9̶0̶  50 ⭐️)",
                                         callback_data=f"buy_stars 100,000 50 ⭐ {model}"),
                ],
                [
                    InlineKeyboardButton(text="1,000,000 токенов (2̶5̶0̶  100 ⭐️)",
                                         callback_data=f"buy_stars 1,000,000 100 {model}"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору модели", callback_data="back_buy_model"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору способа оплаты", callback_data=f"back_buy_method {model}"),
                ]
            ]))
        return
    if GPTModels.GPT_4o.value == model:
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="25,000 токенов (5̶0̶  25 ⭐️)",
                                         callback_data=f"buy_stars 25,000 25 {model}"),
                ],
                [
                    InlineKeyboardButton(text="50,000 токенов (1̶5̶0̶  50 ⭐️)",
                                         callback_data=f"buy_stars 50,000 50 {model}"),
                ],
                [
                    InlineKeyboardButton(text="100,000 токенов (3̶5̶0̶  150 ⭐️)",
                                         callback_data=f"buy_stars 100,000 150 {model}"),
                ],
                [
                    InlineKeyboardButton(text="1,000,000 токенов (1̶5̶0̶0̶  500 ⭐️)",
                                         callback_data=f"buy_stars 1,000,000 500 {model}"),
                ],
                [
                    InlineKeyboardButton(text="2,500,000 токенов (2̶7̶0̶0̶  1000 ⭐️)",
                                         callback_data=f"buy_stars 2,500,000 1000 {model}"),
                ],
                [
                    InlineKeyboardButton(text="5,000,000 токенов (5̶0̶0̶0̶  1700 ⭐️)",
                                         callback_data=f"buy_stars 5,000,000 500 {model}"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору модели", callback_data="back_buy_model"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору способа оплаты", callback_data=f"back_buy_method {model}"),
                ]
            ]))
        return

# Обработчик запроса покупки токенов переводом на счёт
@paymentsRouter.callback_query(StartWithQuery("buy_method_card"))
async def handle_buy_balance_model_query(callback_query: CallbackQuery):
    model = callback_query.data.split(" ")[1]
    await callback_query.message.edit_text("Насколько токенов вы хотите пополнить баланс?")

    if GPTModels.GPT_3_5.value == model:
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="10,000 токенов (40 рублей)",
                                         callback_data=f"buy_card 10,000 40 {model}"),
                ],
                [
                    InlineKeyboardButton(text="50,000 токенов (90 рублей)",
                                         callback_data=f"buy_card 50,000 90 {model}"),
                ],
                [
                    InlineKeyboardButton(text="100,000 токенов (180 рублей)",
                                         callback_data=f"buy_card 100,000 180 {model}"),
                ],
                [
                    InlineKeyboardButton(text="1,000,000 токенов (550 рублей)",
                                         callback_data=f"buy_card 1,000,000 550 {model}"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору модели", callback_data="back_buy_model"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору способа оплаты", callback_data=f"back_buy_method {model}"),
                ]
            ]))
        return

    if GPTModels.GPT_4o.value == model:
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="10,000 токенов (90 рублей)",
                                         callback_data=f"buy_card 10,000 90 {model}"),
                ],
                [
                    InlineKeyboardButton(text="50,000 токенов (250 рублей)",
                                         callback_data=f"buy_card 50,000 250 {model}"),
                ],
                [
                    InlineKeyboardButton(text="100,000 токенов (450 рублей)",
                                         callback_data=f"buy_card 100,000 450 {model}"),
                ],
                [
                    InlineKeyboardButton(text="1,000,000 токенов (2500 рублей)",
                                         callback_data=f"buy_card 1,000,000 2500 {model}"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору модели", callback_data="back_buy_model"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад к выбору способа оплаты", callback_data=f"back_buy_method {model}"),
                ]
            ]))
        return

# Обработчик запроса отправки инвойса (Telegram Stars)
@paymentsRouter.callback_query(StartWithQuery("buy_stars"))
async def handle_buy_balance_model_query(callback_query: CallbackQuery):
    amount = int(callback_query.data.split(" ")[2])
    tokens = callback_query.data.split(" ")[1]
    model = callback_query.data.split(" ")[3]
    await callback_query.message.answer_invoice(
        title="Покупка токенов",
        description=f"Купить {tokens} токенов {model}?",
        prices=[LabeledPrice(label="XTR", amount=amount)],
        provider_token="",
        payload=f"buy_balance {tokens.replace(',', '')} {model} stars",
        currency="XTR",
        reply_markup=payment_keyboard(amount),
    )
    await asyncio.sleep(0.5)
    await callback_query.message.delete()

# Обработчик запроса отправки инвойса (переводом на счёт)
@paymentsRouter.callback_query(StartWithQuery("buy_card"))
async def handle_buy_balance_model_query(callback_query: CallbackQuery):
    amount = int(callback_query.data.split(" ")[2]) * 100
    tokens = callback_query.data.split(" ")[1]
    model = callback_query.data.split(" ")[3]

    await callback_query.bot.send_invoice(
        callback_query.message.chat.id,
        **buy_balance_product,
        description=f"🤩 Покупка {tokens} токенов {model}",
        payload=f"buy_balance {tokens.replace(',', '')} {model} card",
        prices=[types.LabeledPrice(label=f"Покупка {tokens} токенов", amount=amount)]
    )

    await asyncio.sleep(0.5)

    await callback_query.message.delete()

# Обработчик запроса отправки инвойса (пожертвование)
@paymentsRouter.callback_query(StartWithQuery("donation"))
async def handle_change_model_query(callback_query: CallbackQuery):
    amount = int(callback_query.data.split(" ")[1]) * 100

    await callback_query.bot.send_invoice(
        callback_query.message.chat.id,
        **donation_product,
        prices=[types.LabeledPrice(label="Пожертвование на развитие", amount=amount)]
    )

    await asyncio.sleep(0.5)
    await callback_query.message.delete()


@paymentsRouter.pre_checkout_query(lambda query: True)
async def checkout_process(pre_checkout_query: types.PreCheckoutQuery):
    logging.log(logging.INFO, pre_checkout_query)

    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обработчик успешной оплаты
@paymentsRouter.message(F.successful_payment)
async def successful_payment(message: types.Message):
    logging.log(logging.INFO, "SUCCESSFUL PAYMENT:")
    for k, v in message.successful_payment:
        logging.log(logging.INFO, f"{k} = {v}")

    if message.successful_payment.invoice_payload.startswith("donation"):
        await message.answer(
            f"🤩 Платёж на сумму *{message.successful_payment.total_amount // 100} {message.successful_payment.currency}* прошел успешно! 🤩\n\nБлагодарим за поддержку проекта!")
        return

    if message.successful_payment.invoice_payload.startswith("buy_balance"):
        await tokenizeService.get_tokens(message.from_user.id, GPTModels.GPT_3_5)
        await tokenizeService.get_tokens(message.from_user.id, GPTModels.GPT_4o)

        tokens = int(message.successful_payment.invoice_payload.split(" ")[1])
        model = GPTModels(message.successful_payment.invoice_payload.split(" ")[2])
        await tokenizeService.update_user_token(message.from_user.id, model, tokens)

        if message.successful_payment.invoice_payload.split(" ")[3] == "stars": 
            await message.answer(
                f"🤩 Платёж на сумму *{message.successful_payment.total_amount } {message.successful_payment.currency}* прошел успешно! 🤩\n\nВаш баланс пополнен на *{tokens} токенов!*")
        else:
            await message.answer(
                f"🤩 Платёж на сумму *{message.successful_payment.total_amount // 100} {message.successful_payment.currency}* прошел успешно! 🤩\n\nВаш баланс пополнен на *{tokens} токенов!*")

        gpt_35_tokens = await tokenizeService.get_tokens(message.from_user.id, GPTModels.GPT_3_5)
        gpt_4o_tokens = await tokenizeService.get_tokens(message.from_user.id, GPTModels.GPT_4o)

        await message.answer(f"""
        💵 Текущий баланс: 

🤖 `GPT-3.5` : {gpt_35_tokens.get("tokens")} токенов
🦾 `GPT-4o` : {gpt_4o_tokens.get("tokens")} токенов
""")

