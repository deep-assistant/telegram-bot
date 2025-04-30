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
