from aiogram import Router, types, F

import config
from bot.filters import TextCommand
from bot.payment.command_types import payment_command_start
from bot.payment.products import product_test

paymentsRouter = Router()


@paymentsRouter.message(TextCommand(payment_command_start()))
async def buy(message: types.Message):
    if config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await message.answer("Тестовый платеж!!!")

    await message.bot.send_invoice(message.chat.id, **product_test)


@paymentsRouter.pre_checkout_query(lambda query: True)
async def checkout_process(pre_checkout_query: types.PreCheckoutQuery):
    print(pre_checkout_query)
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@paymentsRouter.message(F.successful_payment)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    for k, v in message.successful_payment:
        print(f"{k} = {v}")

    await message.answer(
        f"Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")
