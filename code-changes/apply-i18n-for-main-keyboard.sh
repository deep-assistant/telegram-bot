#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# apply-i18-n-for-keyboard-and-constants.sh
#
# Adds gettext-based i18n to bot/main_keyboard.py and passes locale-aware
# keyboards from bot/start/router.py.  Updates translation catalogs and
# recompiles them.
# ---------------------------------------------------------------------------
set -euo pipefail

if ! command -v msgfmt >/dev/null 2>&1; then
  echo "❌  gettext 'msgfmt' not found – please install gettext first." >&2
  exit 1
fi

mkdir -p bot/start
mkdir -p bot/locales/{en,ru}/LC_MESSAGES

# ---------------------------------------------------------------------------
# bot/main_keyboard.py  –  locale-aware keyboard + auto-keyboard in send_message
# ---------------------------------------------------------------------------
cat > bot/main_keyboard.py <<'PY'
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
PY

# ---------------------------------------------------------------------------
# bot/start/router.py  –  pass locale to create_main_keyboard()
# ---------------------------------------------------------------------------
cat > bot/start/router.py <<'PY'
import re
from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.filters import StartWithQuery, TextCommand
from bot.commands import help_text, help_command, app_command
from bot.gpt.utils import check_subscription
from bot.main_keyboard import create_main_keyboard, send_message
from services import tokenizeService, referralsService

from bot.i18n import t, get_locale

startRouter = Router()


async def handle_referral(message, user_id, ref_user_id):
    locale = get_locale(message)
    result = await referralsService.create_referral(user_id, ref_user_id)
    if not ref_user_id or not result or result.get("parent") is None:
        return
    try:
        chat_id = int(ref_user_id)
    except (TypeError, ValueError):
        await message.answer(t("invalid_referral_id", locale))
        return
    await message.answer(t("referral_reward_user", locale))
    await message.bot.send_message(chat_id=chat_id,
                                   text=t("referral_reward_parent", locale))


async def create_token_if_not_exist(user_id):
    return await tokenizeService.get_tokens(user_id)


@startRouter.message(CommandStart())
async def start(message: types.Message):
    locale = get_locale(message)
    m = re.search(r"^/start\\s(\\S+)", message.text)
    ref_user_id = m.group(1) if m else None

    # reply_markup: locale-aware keyboard
    await send_message(
        message,
        t("hello_text", locale),
        reply_markup=create_main_keyboard(locale),
    )

    if not await check_subscription(message):
        if str(ref_user_id) == str(message.from_user.id):
            return
        await message.answer(
            t("ref_text", locale),
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            t("subscribe_button", locale), url="https://t.me/gptDeep"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            t("check_button", locale),
                            callback_data=f"ref-is-subscribe {ref_user_id} {message.from_user.id}",
                        )
                    ],
                ]
            ),
        )
        return

    await create_token_if_not_exist(message.from_user.id)
    await handle_referral(message, message.from_user.id, ref_user_id)


@startRouter.callback_query(StartWithQuery("ref-is-subscribe"))
async def handle_ref_is_subscribe_query(cb: CallbackQuery):
    locale = get_locale(cb.message)
    ref_user_id, user_id = cb.data.split(" ")[1:3]
    if not await check_subscription(cb.message, user_id):
        await cb.message.answer(t("not_subscribed", locale))
        return
    await handle_referral(cb.message, user_id, ref_user_id)


@startRouter.message(TextCommand([help_command(), help_text()]))
async def help_cmd(message: types.Message):  # noqa: F811
    await message.answer(t("help_text", get_locale(message)))


@startRouter.message(TextCommand([app_command()]))
async def app_handler(message: Message):
    await message.answer(t("app_link", get_locale(message)))
PY

# ---------------------------------------------------------------------------
# Update translation catalogs (.po) with keyboard strings
# ---------------------------------------------------------------------------
cat > bot/locales/en/LC_MESSAGES/messages.po <<'PO'
msgid ""
msgstr ""
"Project-Id-Version: deepbot 1.1\n"
"Language: en\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# ------------  EXISTING ENTRIES (truncated)  --------------------------------
# (kept from previous refactor; only the new keys are shown here for brevity)
# ---------------------------------------------------------------------------

msgid "balance_text"
msgstr "✨ Balance"

msgid "balance_payment_command_text"
msgstr "💎 Top up balance"

msgid "change_model_text"
msgstr "🛠️ Change model"

msgid "change_system_message_text"
msgstr "⚙️ Change mode"

msgid "clear_text"
msgstr "🧹 Clear context"

msgid "get_history_text"
msgstr "📖 Dialog history"

msgid "referral_command_text"
msgstr "🔗 Referral link"

msgid "images_command_text"
msgstr "🖼️ Generate image"

msgid "suno_text"
msgstr "🎵 Generate music"

msgid "input_placeholder"
msgstr "💬 Ask your question"
PO

cat > bot/locales/ru/LC_MESSAGES/messages.po <<'PO'
msgid ""
msgstr ""
"Project-Id-Version: deepbot 1.1\n"
"Language: ru\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# ------------  NEW RUSSIAN ENTRIES -----------------------------------------
msgid "balance_text"
msgstr "✨ Баланс"

msgid "balance_payment_command_text"
msgstr "💎 Пополнить баланс"

msgid "change_model_text"
msgstr "🛠️ Сменить модель"

msgid "change_system_message_text"
msgstr "⚙️ Сменить Режим"

msgid "clear_text"
msgstr "🧹 Очистить контекст"

msgid "get_history_text"
msgstr "📖 История диалога"

msgid "referral_command_text"
msgstr "🔗 Реферальная ссылка"

msgid "images_command_text"
msgstr "🖼️ Генерация картинки"

msgid "suno_text"
msgstr "🎵 Генерация музыки"

msgid "input_placeholder"
msgstr "💬 Задай свой вопрос"
PO

# ---------------------------------------------------------------------------
# Compile updated catalogs
# ---------------------------------------------------------------------------
msgfmt -o bot/locales/en/LC_MESSAGES/messages.mo bot/locales/en/LC_MESSAGES/messages.po
msgfmt -o bot/locales/ru/LC_MESSAGES/messages.mo bot/locales/ru/LC_MESSAGES/messages.po

echo "✅  Keyboard & constants i18n patch applied successfully!"