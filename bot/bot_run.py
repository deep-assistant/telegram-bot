import asyncio
import logging
import aiohttp
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import config
from bot.agreement import agreementRouter
from bot.api.router import apiRouter
from bot.gpt import gptRouter
from bot.image_editing import imageEditingRouter
from bot.images import imagesRouter
from bot.payment import paymentsRouter
from bot.referral.router import referralRouter
from bot.start import startRouter
from bot.suno import sunoRouter
from bot.tasks import taskRouter
from bot.diagnostics import diagnosticsRouter
from bot.middlewares import WebhookSecurityMiddleware


def apply_routers(dp: Dispatcher) -> None:
    dp.include_router(imagesRouter)
    dp.include_router(sunoRouter)
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


# Connection pool manager for better throughput
@asynccontextmanager
async def create_session():
    """Create optimized aiohttp session with connection pooling."""
    connector = aiohttp.TCPConnector(
        limit=100,  # Total connection pool size
        limit_per_host=30,  # Per-host connection limit
        keepalive_timeout=30,  # Keep connections alive for 30 seconds
        enable_cleanup_closed=True,  # Clean up closed connections
        use_dns_cache=True,  # Cache DNS lookups
    )
    
    timeout = aiohttp.ClientTimeout(total=30, connect=5)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={'User-Agent': 'TelegramBot/1.0'}
    ) as session:
        yield session


# Enhanced startup and shutdown hooks for webhook mode.
async def on_startup(dp: Dispatcher):
    logging.info("Bot is starting...")
    if config.WEBHOOK_ENABLED:
        # Configure webhook with additional options for better throughput
        webhook_info = await dp.bot.get_webhook_info()
        if webhook_info.url != config.WEBHOOK_URL:
            await dp.bot.set_webhook(
                url=config.WEBHOOK_URL,
                drop_pending_updates=True,
                max_connections=getattr(config, 'WEBHOOK_MAX_CONNECTIONS', 40),
                secret_token=getattr(config, 'WEBHOOK_SECRET_TOKEN', None)
            )
            logging.info(f"Webhook set to: {config.WEBHOOK_URL}")
        else:
            logging.info("Webhook already configured correctly")


async def on_shutdown(dp: Dispatcher):
    logging.info("Bot is shutting down...")
    if config.WEBHOOK_ENABLED:
        await dp.bot.delete_webhook()
        logging.info("Webhook deleted")


async def create_webhook_app(dp: Dispatcher, bot: Bot) -> web.Application:
    """Create optimized webhook application with performance enhancements."""
    app = web.Application()
    
    # Add health check endpoint
    async def health_check(request):
        return web.json_response({
            'status': 'healthy',
            'timestamp': asyncio.get_event_loop().time(),
            'webhook_url': config.WEBHOOK_URL
        })
    
    # Add metrics endpoint (if enabled)
    if getattr(config, 'WEBHOOK_METRICS_ENABLED', False):
        webhook_middleware = None
        for middleware in dp.message.middlewares:
            if isinstance(middleware, WebhookSecurityMiddleware):
                webhook_middleware = middleware
                break
        
        async def metrics(request):
            if webhook_middleware:
                return web.json_response(webhook_middleware.get_metrics())
            return web.json_response({'error': 'Metrics not available'})
        
        app.router.add_get('/metrics', metrics)
    
    app.router.add_get('/health', health_check)
    
    # Setup webhook handler
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=config.WEBHOOK_PATH)
    
    return app


async def bot_run() -> None:
    # Configure logging
    logging.basicConfig(
        level=getattr(config, 'LOG_LEVEL', logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Add security middleware for webhook mode
    if config.WEBHOOK_ENABLED:
        dp.message.middleware(WebhookSecurityMiddleware())
    
    dp.message.middleware(AlbumMiddleware())
    apply_routers(dp)

    # Create optimized session for better performance
    async with create_session() as session:
        # Initialize the bot based on the development flag.
        if config.IS_DEV:
            bot = Bot(
                token=config.TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
                session=AiohttpSession(session=session)
            )
        else:
            bot = Bot(
                token=config.TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
                session=AiohttpSession(
                    api=TelegramAPIServer.from_base(config.ANALYTICS_URL),
                    session=session
                )
            )

        # Choose between webhook and polling modes.
        if config.WEBHOOK_ENABLED:
            # Create optimized webhook application
            app = await create_webhook_app(dp, bot)
            
            # Start webhook mode with enhanced configuration
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(
                runner,
                host=config.WEBHOOK_HOST,
                port=config.WEBHOOK_PORT,
                reuse_address=True,
                reuse_port=True,  # Enable SO_REUSEPORT for better performance
            )
            
            await on_startup(dp)
            await site.start()
            
            logging.info(f"Webhook server started on {config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}")
            logging.info(f"Webhook URL: {config.WEBHOOK_URL}")
            logging.info(f"Health check: http://{config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}/health")
            
            try:
                # Keep the server running
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logging.info("Received shutdown signal")
            finally:
                await on_shutdown(dp)
                await runner.cleanup()
        else:
            # Delete webhook if exists and start polling.
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                skip_updates=False,
                drop_pending_updates=True
            )