from aiogram import types, Router
from aiogram.filters import CommandStart

from bot.payment.command_types import payment_command_start

startRouter = Router()


@startRouter.message(CommandStart())
async def buy(message: types.Message):
    kb = [[types.KeyboardButton(text=payment_command_start()),]]

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)

    await message.answer("Hello", reply_markup=keyboard)
