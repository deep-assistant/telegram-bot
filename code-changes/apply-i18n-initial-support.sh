#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# apply_i18n_initial_support.sh
# ---------------------------------------------------------------------------
set -euo pipefail

# -- check dependencies ------------------------------------------------------
if ! command -v msgfmt >/dev/null 2>&1; then
  echo "❌  gettext 'msgfmt' not found.  Install gettext and try again." >&2
  exit 1
fi

# -- lay out folders ---------------------------------------------------------
mkdir -p bot/start
mkdir -p bot/locales/{en,ru}/LC_MESSAGES

# -- bot/i18n.py -------------------------------------------------------------
cat > bot/i18n.py <<'PY'
import gettext
from pathlib import Path
from typing import Dict

LANG_DEFAULT = "en"
_LOCALES_DIR = Path(__file__).resolve().parent / "locales"
_CACHE: Dict[str, gettext.GNUTranslations] = {}


def _gt(locale: str) -> gettext.GNUTranslations:
    if locale not in _CACHE:
        _CACHE[locale] = gettext.translation(
            domain="messages",
            localedir=_LOCALES_DIR,
            languages=[locale],
            fallback=True,
        )
    return _CACHE[locale]


def t(msgid: str, locale: str) -> str:
    return _gt(locale).gettext(msgid)


def get_locale(message) -> str:
    lang = (getattr(message.from_user, "language_code", "") or "").lower()
    return "ru" if lang.startswith("ru") else "en"
PY

# -- bot/start/router.py -----------------------------------------------------
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

    await send_message(message, t("hello_text", locale),
                       reply_markup=create_main_keyboard())

    if not await check_subscription(message):
        if str(ref_user_id) == str(message.from_user.id):
            return
        await message.answer(
            t("ref_text", locale),
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(t("subscribe_button", locale),
                                                url="https://t.me/gptDeep")],
                    [types.InlineKeyboardButton(t("check_button", locale),
                                                callback_data=f"ref-is-subscribe {ref_user_id} {message.from_user.id}")]
                ]
            ),
        )
        return

    await create_token_if_not_exist(message.from_user.id)
    await handle_referral(message, message.from_user.id, ref_user_id)


@startRouter.callback_query(StartWithQuery("ref-is-subscribe"))
async def handle_ref_is_subscribe_query(callback_query: CallbackQuery):
    locale = get_locale(callback_query.message)
    ref_user_id, user_id = callback_query.data.split(" ")[1:3]
    if not await check_subscription(callback_query.message, user_id):
        await callback_query.message.answer(t("not_subscribed", locale))
        return
    await handle_referral(callback_query.message, user_id, ref_user_id)


@startRouter.message(TextCommand([help_command(), help_text()]))
async def help_cmd(message: types.Message):  # noqa: F811
    await message.answer(t("help_text", get_locale(message)))


@startRouter.message(TextCommand([app_command()]))
async def app_handler(message: Message):
    await message.answer(t("app_link", get_locale(message)))
PY

# -- English messages --------------------------------------------------------
cat > bot/locales/en/LC_MESSAGES/messages.po <<'PO'
msgid ""
msgstr ""
"Project-Id-Version: deepbot 1.0\n"
"Language: en\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "hello_text"
msgstr ""
"👋 Hi! I'm a bot from the developers of deep.foundation!\n"
"\n"
"🤖 I'm ready to help you with any task — just send a message or press a menu button!\n"
"\n"
"/help - ✨ overview of commands and features\n"
"/balance - ⚡️ check your balance\n"
"/referral - 🔗 referral program details\n"
"\n"
"Everything is free unless you pay.\n"
"Every day your balance will be topped up by *10 000⚡️* (energy)!\n"
"\n"
"Need more?\n"
"💎 Top up your balance with Telegram Stars or a bank card.\n"
"👥 Enjoy the bot? Share it with friends and get a bonus for each one you invite! Bring lots of friends and you'll be able to use neural networks almost without limits.\n"
"\n"
"/referral - earn more with the referral system:\n"
"*5 000⚡️* for each invited user;\n"
"*+500⚡️* to the daily top-up for each friend.\n"
"\n"
"🏠 If something went wrong or you’d like to share inspiration, write to our community @deepGPT."

msgid "ref_text"
msgstr "👋 You came via a referral link. To claim your reward, please subscribe to my channel."

msgid "referral_reward_user"
msgstr ""
"🎉 You received *5 000*⚡️!\n"
"\n"
"/balance - ✨ Check balance\n"
"/referral - 🔗 Referral details"

msgid "referral_reward_parent"
msgstr ""
"🎉 A new referral has been added!\n"
"You received *5 000*⚡️!\n"
"Your referral must do any activity in the bot within 24 h for you to get another *5 000*⚡️ and +500⚡️ to your daily top-up.\n"
"\n"
"/balance - ✨ Check balance\n"
"/referral - 🔗 Referral details"

msgid "subscribe_button"
msgstr "Subscribe 👊🏻"

msgid "check_button"
msgstr "Check ✅"

msgid "not_subscribed"
msgstr "You haven't subscribed! 😡"

msgid "invalid_referral_id"
msgstr "❌ Invalid referral ID."

msgid "help_text"
msgstr ""
"The main resource for accessing neural networks is ⚡️ (energy) — a universal resource for all bot functions.\n"
"\n"
"Each neural network consumes a different amount of ⚡️.\n"
"The cost depends on dialog history length, chosen models, and the size of your questions and the network’s answers.\n"
"To save ⚡️, use /clear so the dialog history doesn’t overflow and increase consumption!\n"
"It’s recommended to clear the context before starting a new topic and also if the selected model starts refusing to help.\n"
"\n"
"/app - 🔥 Get the application link!\n"
"/start - 🔄 Restart the bot to update to the latest version.\n"
"/model - 🛠️ Switch the model.\n"
"/system - ⚙️ System message to change the interaction mode.\n"
"/clear - 🧹 Clear the context.\n"
"/balance - ✨ Balance.\n"
"/image - 🖼️ Image generation (Midjourney, DALL·E 3, Flux, Stable Diffusion)\n"
"/buy - 💎 Top up the balance.\n"
"/referral - 🔗 Get a referral link\n"
"/suno - 🎵 Music generation (Suno)\n"
"/text - Send a text message"

msgid "app_link"
msgstr "Application link: https://t.me/DeepGPTBot/DeepGPT"
PO

# -- Russian messages --------------------------------------------------------
cat > bot/locales/ru/LC_MESSAGES/messages.po <<'PO'
msgid ""
msgstr ""
"Project-Id-Version: deepbot 1.0\n"
"Language: ru\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "hello_text"
msgstr ""
"👋 Привет! Я бот от разработчиков deep.foundation!\n"
"\n"
"🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение или нажми кнопку в меню!\n"
"\n"
"/help - ✨ обзор команд и возможностей\n"
"/balance - ⚡️ узнать свой баланс\n"
"/referral - 🔗 подробности рефералки\n"
"\n"
"Всё бесплатно, если не платить.\n"
"Каждый день твой баланс будет пополняться на сумму от *10 000⚡️* (энергии)!\n"
"\n"
"Если нужно больше:\n"
"💎 Можно пополнить баланс Telegram звёздами или банковской картой.\n"
"👥 Понравилось? Поделись с друзьями и получи бонус за каждого приглашенного друга! Приводя много друзей ты сможешь пользоваться нейросетями практически безлимитно.\n"
"\n"
"/referral - получай больше с реферальной системой:\n"
"*5 000⚡️️* за каждого приглашенного пользователя;\n"
"*+500⚡️️* к ежедневному пополнению баланса за каждого друга.\n"
"\n"
"🏠 Если что-то пошло не так или хочешь поделиться вдохновением, напиши в наше сообщество @deepGPT."

msgid "ref_text"
msgstr "👋 Ты прибыл по реферальной ссылке, чтобы получить награду нужно подписаться на мой канал."

msgid "referral_reward_user"
msgstr ""
"🎉 Вы получили *5 000*⚡️!\n"
"\n"
"/balance - ✨ Узнать баланс\n"
"/referral - 🔗 Подробности рефералки"

msgid "referral_reward_parent"
msgstr ""
"🎉 Добавлен новый реферал!\n"
"Вы получили *5 000*⚡️!\n"
"Ваш реферал должен проявить любую активность в боте через 24 часа, чтобы вы получили еще *5 000*⚡️ и +500⚡️️ к ежедневному пополнению баланса.\n"
"\n"
"/balance - ✨ Узнать баланс\n"
"/referral - 🔗 Подробности рефералки"

msgid "subscribe_button"
msgstr "Подписаться 👊🏻"

msgid "check_button"
msgstr "Проверить ✅"

msgid "not_subscribed"
msgstr "Вы не подписались! 😡"

msgid "invalid_referral_id"
msgstr "❌ Некорректный реферальный ID."

msgid "help_text"
msgstr ""
"Основной ресурc для доступа к нейросетям - ⚡️ (энергия).\n"
"Это универсальный ресурс для всего функционала бота.\n"
"\n"
"Каждая нейросеть тратит разное количество ⚡️.\n"
"Количество затраченных ⚡️ зависит от длины истории диалога, моделей нейросетей и объёма ваших вопросов и ответов от нейросети.\n"
"Для экономии используйте команду - /clear, чтобы не переполнять историю диалога и не увеличивать расход ⚡️ (энергии)!\n"
"Рекомендуется очищать контекст перед началом обсуждения новой темы. А также если выбранная модель начала отказывать в помощи.\n"
"\n"
"/app - 🔥 Получить ссылку к приложению!\n"
"/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.\n"
"/model - 🛠️ Сменить модель, перезапускает бот, позволяет сменить модель бота.\n"
"/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить режим взаимодействия с ботом.\n"
"/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.\n"
"/balance - ✨ Баланс, позволяет узнать баланс ⚡️.\n"
"/image - 🖼️ Генерация картинки (Midjourney, DALL·E 3, Flux, Stable Diffusion)\n"
"/buy - 💎 Пополнить баланс, позволяет пополнить баланс ⚡️.\n"
"/referral - 🔗 Получить реферальную ссылку\n"
"/suno - 🎵 Генерация музыки (Suno)\n"
"/text - Отправить текстовое сообщение"

msgid "app_link"
msgstr "Ссылка на приложение: https://t.me/DeepGPTBot/DeepGPT"
PO

# -- compile to .mo ----------------------------------------------------------
msgfmt -o bot/locales/en/LC_MESSAGES/messages.mo bot/locales/en/LC_MESSAGES/messages.po
msgfmt -o bot/locales/ru/LC_MESSAGES/messages.mo bot/locales/ru/LC_MESSAGES/messages.po

echo "✅  i18n refactor applied and catalogs compiled successfully!"