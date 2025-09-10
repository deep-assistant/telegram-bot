import asyncio

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from bot.agreement import agreementRouter
from bot.api.router import apiRouter
from bot.gpt import gptRouter
from bot.image_editing import imageEditingRouter
from bot.images import imagesRouter
from bot.payment import paymentsRouter
from bot.referral.router import referralRouter
from bot.search import searchRouter
from bot.start import startRouter
from bot.suno import sunoRouter
from bot.tasks import taskRouter
from bot.diagnostics import diagnosticsRouter


def apply_routers(dp: Dispatcher) -> None:
    dp.include_router(imagesRouter)
    dp.include_router(sunoRouter)
    dp.include_router(searchRouter)
    dp.include_router(startRouter)
    dp.include_router(diagnosticsRouter)
    dp.include_router(referralRouter)
    dp.include_router(paymentsRouter)
    dp.include_router(apiRouter)
    dp.include_router(agreementRouter)
    dp.include_router(imageEditingRouter)
    dp.include_router(taskRouter)
    dp.include_router(gptRouter)

# todo пофиксить
class AlbumMiddleware(BaseMiddleware):
    album_data = {}
    batch_data = {}

    async def __call__(self, handler, event, data):
        if event.photo is None:
            date = str(event.date)
            print(date)

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


# Startup and shutdown hooks for webhook mode.
async def on_startup(dp: Dispatcher):
    print("Bot is starting...")
    if config.WEBHOOK_ENABLED:
        await dp.bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown(dp: Dispatcher):
    print("Bot is shutting down...")
    if config.WEBHOOK_ENABLED:
        await dp.bot.delete_webhook()


async def bot_run() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AlbumMiddleware())
    apply_routers(dp)

    # Initialize the bot based on the development flag.
    if config.IS_DEV:
        bot = Bot(
            token=config.TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        )
    else:
        bot = Bot(
            token=config.TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
            session=AiohttpSession(
                api=TelegramAPIServer.from_base(config.ANALYTICS_URL)
            )
        )

    # Choose between webhook and polling modes.
    if config.WEBHOOK_ENABLED:
        # Set webhook and start webhook mode.
        await bot.set_webhook(config.WEBHOOK_URL)
        await dp.start_webhook(
            webhook_path=config.WEBHOOK_PATH,  # e.g., '/webhook'
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host=config.WEBHOOK_HOST,          # e.g., '0.0.0.0'
            port=config.WEBHOOK_PORT           # e.g., 3000
        )
    else:
        # Delete webhook if exists and start polling.
        await bot.delete_webhook()
        await dp.start_polling(
            bot,
            skip_updates=False,
            drop_pending_updates=True
        )