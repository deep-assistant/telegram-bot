import asyncio
import logging

from bot.bot_run import bot_run

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(bot_run())
