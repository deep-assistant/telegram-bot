from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from bot.utils import include
from services import StateTypes, stateService


class TextCommand(BaseFilter):
    def __init__(self, text_command: [str]):
        self.text_command: [str] = text_command

    async def __call__(self, message: Message) -> bool:
        if message.text is None:
            return False

        return include(self.text_command, message.text)


class Document(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.document is not None


class Photo(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.photo is not None


class Voice(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        print(message)
        return message.voice is not None


class StartWithQuery(BaseFilter):
    def __init__(self, text_command: str):
        self.text_command: str = text_command

    async def __call__(self, callback_query: CallbackQuery) -> bool:
        return callback_query.data.startswith(self.text_command)


class TextCommandQuery(BaseFilter):
    def __init__(self, text_command: [str]):
        self.text_command: [str] = text_command

    async def __call__(self, callback_query: CallbackQuery) -> bool:
        return include(self.text_command, callback_query.data)


class StateCommand(BaseFilter):
    def __init__(self, state: StateTypes):
        self.state: StateTypes = state

    async def __call__(self, message: Message) -> bool:
        return stateService.get_current_state(message.from_user.id).value == self.state.value
