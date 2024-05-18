from aiogram.filters import BaseFilter
from aiogram.types import Message


class TextCommand(BaseFilter):  # [1]
    def __init__(self, text_command: str):  # [2]
        self.text_command = text_command

    async def __call__(self, message: Message) -> bool:  # [3]
        return message.text == self.text_command
