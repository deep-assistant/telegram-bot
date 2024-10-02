from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.gpt.utils import checked_text
from services.gpt_service import SystemMessages

from .db_system_message import default_system_message, happy_system_message, software_developer_system_message, question_answer_mode, promt_deep

system_messages = {
    SystemMessages.Default.value: default_system_message,
    SystemMessages.Happy.value: happy_system_message,
    SystemMessages.SoftwareDeveloper.value: software_developer_system_message,
    SystemMessages.DeepPromt.value: promt_deep,
    SystemMessages.QuestionAnswer.value: question_answer_mode
}

text_system_messages = {
    SystemMessages.Custom.value: "💎 Указать свое",
    SystemMessages.Default.value: "🤖 Стандартный",
    SystemMessages.Happy.value: "🥳 Веселый",
    SystemMessages.SoftwareDeveloper.value: "👨‍💻 Программист",
    SystemMessages.DeepPromt.value: "🕳️ Wanderer from the Deep",
    SystemMessages.QuestionAnswer.value: "💬 Вопрос-ответ"
}


def get_system_message(value: str) -> str:
    if value in system_messages:
        return system_messages[value]

    return value


system_messages_list = list(map(lambda message: message.value, SystemMessages))


def get_system_message_text(system_message: str, current_system_message: str):
    if system_message == current_system_message:
        return checked_text(system_message)

    return system_message


def create_system_message_keyboard(current_system_message: str):
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_system_message_text(
                    text_system_messages[SystemMessages.Custom.value],
                    text_system_messages[current_system_message]
                ),
                callback_data=SystemMessages.Custom.value
            )
        ],
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
            InlineKeyboardButton(
                text=get_system_message_text(
                    text_system_messages[SystemMessages.DeepPromt.value],
                    text_system_messages[current_system_message]
                ),
                callback_data=SystemMessages.DeepPromt.value
            )
        ],
        [
            InlineKeyboardButton(
                text=get_system_message_text(
                    text_system_messages[SystemMessages.QuestionAnswer.value],
                    text_system_messages[current_system_message]
                ),
                callback_data=SystemMessages.QuestionAnswer.value
            )
        ]
    ])
