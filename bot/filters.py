from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.utils import include


class TextCommand(BaseFilter):
    def __init__(self, text_command: [str]):
        self.text_command: [str] = text_command

    async def __call__(self, message: Message) -> bool:
        return include(self.text_command, message.text)


class Document(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.document is not None


class Photo(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.photo is not None
