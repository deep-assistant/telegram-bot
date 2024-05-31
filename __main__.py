import asyncio
import logging

from bot.bot_run import bot_run
from services import run_init_reset

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_init_reset()
    asyncio.run(bot_run())
