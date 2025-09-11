from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.gpt.utils import checked_text
from services.gpt_service import SystemMessages
from services.repository_service import repositoryService

from .db_system_message import default_system_message, happy_system_message, software_developer_system_message, question_answer_mode, promt_deep, transcribe

system_messages = {
    SystemMessages.Default.value: default_system_message,
    SystemMessages.Happy.value: happy_system_message,
    SystemMessages.SoftwareDeveloper.value: software_developer_system_message,
    SystemMessages.DeepPromt.value: promt_deep,
    SystemMessages.QuestionAnswer.value: question_answer_mode,
    SystemMessages.Transcribe.value: transcribe
}

text_system_messages = {
    SystemMessages.Custom.value: "💎 Указать свое",
    SystemMessages.Default.value: "🤖 Стандартный",
    SystemMessages.Happy.value: "🥳 Веселый",
    SystemMessages.SoftwareDeveloper.value: "👨‍💻 Программист",
    SystemMessages.DeepPromt.value: "🕳️ Wanderer from the Deep",
    SystemMessages.QuestionAnswer.value: "💬 Вопрос-ответ",
    SystemMessages.Transcribe.value: "🎤 Голос в текст"
}


def get_system_message(value: str) -> str:
    if value in system_messages:
        return system_messages[value]

    return value


def get_system_message_with_context(value: str, user_id: str) -> str:
    """Get system message with repository context if available"""
    base_message = get_system_message(value)
    
    # Get repository context for the user
    repository_url = repositoryService.get_current_repository(user_id)
    if repository_url:
        repository_context = repositoryService.format_repository_context(repository_url)
        return base_message + repository_context
    
    return base_message


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
        ],
        [
            InlineKeyboardButton(
                text=get_system_message_text(
                    text_system_messages[SystemMessages.Transcribe.value],
                    text_system_messages[current_system_message]
                ),
                callback_data=SystemMessages.Transcribe.value
            )
        ]
    ])
