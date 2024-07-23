import asyncio

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from bot.agreement import agreementRouter
from bot.gpt import gptRouter
from bot.images import imagesRouter
from bot.payment import paymentsRouter
from bot.referral.router import referralRouter
from bot.start import startRouter


def apply_routers(dp: Dispatcher) -> None:
    dp.include_router(referralRouter)
    dp.include_router(imagesRouter)
    dp.include_router(startRouter)
    dp.include_router(agreementRouter)
    dp.include_router(paymentsRouter)
    dp.include_router(gptRouter)


# todo пофиксить
class AlbumMiddleware(BaseMiddleware):
    album_data = {}
    batch_data = {}

    async def __call__(self, handler, event, data):
        if event.photo is None:
            date = str(event.date)

            try:
                self.batch_data[date].append(event)
                return
            except KeyError:
                self.batch_data[date] = [event]

            await asyncio.sleep(0.01)
            event.model_config["is_last"] = True
            data["batch_messages"] = self.batch_data[date]

            result = await handler(event, data)

            if event.model_config.get("is_last"):
                del self.batch_data[date]

            return result

        if not event.media_group_id:
            if event.photo is not None:
                data["album"] = [event]

            return await handler(event, data)

        try:
            self.album_data[event.media_group_id].append(event)
            return
        except KeyError:
            self.album_data[event.media_group_id] = [event]

        await asyncio.sleep(0.01)
        event.model_config["is_last"] = True
        data["album"] = self.album_data[event.media_group_id]

        result = await handler(event, data)

        if event.media_group_id and event.model_config.get("is_last"):
            del self.album_data[event.media_group_id]

        return result


async def bot_run() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AlbumMiddleware())

    if config.IS_DEV:
        bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

        apply_routers(dp)

        await bot.delete_webhook()
        await dp.start_polling(bot, skip_updates=False, drop_pending_updates=True)
        return

    bot = Bot(
        token=config.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        session=AiohttpSession(
            api=TelegramAPIServer.from_base(config.ANALYTICS_URL)
        )
    )

    apply_routers(dp)

    await bot.delete_webhook()
    await dp.start_polling(bot, skip_updates=False, drop_pending_updates=True)
