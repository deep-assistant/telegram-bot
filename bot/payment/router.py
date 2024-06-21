import asyncio
import logging

from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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


@paymentsRouter.message(TextCommand([payment_command_start(), payment_command_text()]))
async def buy(message: types.Message):
    await message.answer(
        text=donation_text,
        reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
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
            ])
    )


def create_buy_balance_keyboard():
    return InlineKeyboardMarkup(
        resize_keyboard=True,

        inline_keyboard=[
            [
                InlineKeyboardButton(text="🤖 GPT-4o", callback_data=f"buy-gpt {GPTModels.GPT_4o.value}"),
                InlineKeyboardButton(text="🦾 GPT-3.5", callback_data=f"buy-gpt {GPTModels.GPT_3_5.value}"),
            ],
        ])


@paymentsRouter.callback_query(StartWithQuery("back_buy_model"))
async def handle_buy_balance_query(callback_query: CallbackQuery):
    await callback_query.message.edit_text(text="Баланс какой модели вы хотите пополнить?")
    await callback_query.message.edit_reply_markup(reply_markup=create_buy_balance_keyboard())


@paymentsRouter.message(TextCommand([balance_payment_command_text(), balance_payment_command_start()]))
async def buy_balance(message: types.Message):
    await message.answer(text="Баланс какой модели вы хотите пополнить?", reply_markup=create_buy_balance_keyboard())


@paymentsRouter.callback_query(StartWithQuery("buy-gpt"))
async def handle_buy_balance_model_query(callback_query: CallbackQuery):
    model = callback_query.data.split(" ")[1]

    await callback_query.message.edit_text("Насколько токенов вы хотите пополнить баланс?")

    if GPTModels.GPT_3_5.value == model:
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="10,000 токенов (40 рублей)",
                                         callback_data=f"buy 10,000 40 {model}"),
                ],
                [
                    InlineKeyboardButton(text="50,000 токенов (90 рублей)",
                                         callback_data=f"buy 50,000 90 {model}"),
                ],
                [
                    InlineKeyboardButton(text="100,000 токенов (180 рублей)",
                                         callback_data=f"buy 100,000 180 {model}"),
                ],
                [
                    InlineKeyboardButton(text="1,000,000 токенов (550 рублей)",
                                         callback_data=f"buy 1,000,000 550 {model}"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад", callback_data="back_buy_model"),
                ]
            ]))
        return

    if GPTModels.GPT_4o.value == model:
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="10,000 токенов (90 рублей)",
                                         callback_data=f"buy 10,000 90 {model}"),
                ],
                [
                    InlineKeyboardButton(text="50,000 токенов (250 рублей)",
                                         callback_data=f"buy 50,000 250 {model}"),
                ],
                [
                    InlineKeyboardButton(text="100,000 токенов (450 рублей)",
                                         callback_data=f"buy 100,000 450 {model}"),
                ],
                [
                    InlineKeyboardButton(text="1,000,000 токенов (2500 рублей)",
                                         callback_data=f"buy 1,000,000 2500 {model}"),
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад", callback_data="back_buy_model"),
                ]
            ]))
        return


@paymentsRouter.callback_query(StartWithQuery("buy"))
async def handle_buy_balance_model_query(callback_query: CallbackQuery):
    amount = int(callback_query.data.split(" ")[2]) * 100
    tokens = callback_query.data.split(" ")[1]
    model = callback_query.data.split(" ")[3]

    await callback_query.bot.send_invoice(
        callback_query.message.chat.id,
        **buy_balance_product,
        description=f"🤩 Покупка {tokens} токенов {model}",
        payload=f"buy_balance {tokens.replace(',', '')} {model}",
        prices=[types.LabeledPrice(label=f"Покупка {tokens} токенов", amount=amount)]
    )

    await asyncio.sleep(0.5)

    await callback_query.message.delete()


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
        tokenizeService.update_user_token(message.from_user.id, GPTModels(message.successful_payment.invoice_payload.split(" ")[2]), int(message.successful_payment.invoice_payload.split(" ")[1]))

        await message.answer(
            f"🤩 Платёж на сумму *{message.successful_payment.total_amount // 100} {message.successful_payment.currency}* прошел успешно!")

        gpt_35_tokens = tokenizeService.get_tokens(message.from_user.id, GPTModels.GPT_3_5)
        gpt_4o_tokens = tokenizeService.get_tokens(message.from_user.id, GPTModels.GPT_4o)

        await message.answer(f"""
        💵 Текущий баланс: 

🤖  `GPT-3.5` : {gpt_35_tokens.get("tokens")} токенов
🦾  `GPT-4o` : {gpt_4o_tokens.get("tokens")} токенов
""")
