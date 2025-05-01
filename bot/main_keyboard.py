from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery

from bot.i18n import t, get_locale

# Track how many messages we’ve sent in each chat (since bot start-up)
chat_message_counts: dict[int, int] = {}

FIRST_MESSAGES_LIMIT = 3


def create_main_keyboard(locale: str | None = None) -> ReplyKeyboardMarkup:
    """
    Build the main reply-keyboard in the requested *locale*.
    If locale is None we fall back to English.
    """
    locale = locale or "en"
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text=t("balance_text", locale)),
                KeyboardButton(text=t("balance_payment_command_text", locale)),
            ],
            [
                KeyboardButton(text=t("change_model_text", locale)),
                KeyboardButton(text=t("change_system_message_text", locale)),
            ],
            [
                KeyboardButton(text=t("suno_text", locale)),
                KeyboardButton(text=t("images_command_text", locale)),
            ],
            [
                KeyboardButton(text=t("clear_text", locale)),
                KeyboardButton(text=t("get_history_text", locale)),
            ],
            [
                KeyboardButton(text=t("referral_command_text", locale)),
            ],
        ],
        input_field_placeholder=t("input_placeholder", locale),
    )


async def send_message(callback_or_message: Message | CallbackQuery, *args, **kwargs):
    """
    A helper that mirrors Message.answer but auto-injects the main keyboard in
    the first few bot replies of every chat.
    """

    if isinstance(callback_or_message, Message):
        chat_id = callback_or_message.chat.id
        responder = callback_or_message.answer
        src_for_locale = callback_or_message
    elif isinstance(callback_or_message, CallbackQuery):
        chat_id = callback_or_message.message.chat.id
        responder = callback_or_message.message.answer
        src_for_locale = callback_or_message.message
    else:
        raise ValueError("First argument must be Message or CallbackQuery")

    # determine locale of the user
    locale = get_locale(src_for_locale)

    # count messages
    chat_message_counts[chat_id] = chat_message_counts.get(chat_id, 0) + 1

    # auto-keyboard if no explicit markup & within the first N messages
    if "reply_markup" not in kwargs and chat_message_counts[chat_id] <= FIRST_MESSAGES_LIMIT:
        kwargs["reply_markup"] = create_main_keyboard(locale)

    await responder(*args, **kwargs)
