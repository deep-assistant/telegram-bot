from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.gpt.utils import checked_text
from services.gpt_service import SystemMessages

default_system_message = ""

happy_system_message = """
Отвечай, как обычно, только чуть-чуть прикалывайся, матерись, обращайся к пользователю на ты, прикидывайся придурком
"""

software_developer_system_message = """Выполняй роль программиста с огромным опытом на абсолютно разных языках, твоя роль это помогать с кодом, объяснять нюансы"""

system_messages = {
    SystemMessages.Default.value: default_system_message,
    SystemMessages.Happy.value: happy_system_message,
    SystemMessages.SoftwareDeveloper.value: software_developer_system_message,
}

text_system_messages = {
    SystemMessages.Default.value: "🤖 Стандартный",
    SystemMessages.Happy.value: "🥳 Веселый",
    SystemMessages.SoftwareDeveloper.value: "👨‍💻 Программист",
}


def get_system_message(value: str) -> str:
    if value in system_messages:
        return system_messages[value]

    return value


system_messages_list = list(map(lambda message: message.value, SystemMessages))


def get_system_message_text(system_message: str, current_system_message: str):
    print(system_message)
    print(current_system_message)
    if system_message == current_system_message:
        return checked_text(system_message)

    return system_message


def create_system_message_keyboard(current_system_message: str):
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_system_message_text(
                    text_system_messages[SystemMessages.Default.value],
                    text_system_messages[current_system_message]
                ),
                callback_data=SystemMessages.Default.value
            ),
            InlineKeyboardButton(
                text=get_system_message_text(
                    text_system_messages[SystemMessages.Happy.value],
                    text_system_messages[current_system_message]
                ),
                callback_data=SystemMessages.Happy.value
            )
        ],
        [
            InlineKeyboardButton(
                text=get_system_message_text(
                    text_system_messages[SystemMessages.SoftwareDeveloper.value],
                    text_system_messages[current_system_message]
                ),
                callback_data=SystemMessages.SoftwareDeveloper.value
            ),
        ]
    ])
