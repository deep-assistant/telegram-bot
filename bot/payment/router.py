import asyncio
import logging

from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot.filters import TextCommand
from bot.payment.command_types import payment_command_start, payment_command_text
from bot.payment.products import donation_product

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
                ]
            ])
    )


@paymentsRouter.callback_query()
async def handle_change_model_query(callback_query: CallbackQuery):
    if (callback_query.data.startswith("donation")):
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

    await message.answer(
        f"Платёж на сумму **{message.successful_payment.total_amount // 100} {message.successful_payment.currency}** прошел успешно! 🤩\n\nБлагодарим за поддержку проекта!")
