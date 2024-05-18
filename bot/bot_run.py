from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from bot.payment.router import paymentsRouter
from bot.start.router import startRouter


def apply_routers(dp: Dispatcher) -> None:
    dp.include_router(startRouter)
    dp.include_router(paymentsRouter)


async def bot_run() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)

    apply_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=False)
