import logging

from aiogram import Router, types

from bot.filters import TextCommand
from bot.referral.command_types import referral_command, referral_command_text
from services import referralsService

referralRouter = Router()


@referralRouter.message(TextCommand([referral_command(), referral_command_text()]))
async def handle_start_referral_generation(message: types.Message):

    bot_info = await message.bot.get_me()
    user_id = message.from_user.id
    referral_link = f"https://t.me/{bot_info.username}?start={user_id}"

    logging.info(f"Generated referral link for user {user_id}: {referral_link}")

    await message.bot.send_chat_action(message.chat.id, "typing")

    referral = await referralsService.get_referral(message.from_user.id)

    await message.answer(f"""
*15 000* `energy` ⚡ за каждого приглашенного пользователя. 
*+500* `energy` ⚡ к ежедневному пополнению баланса за каждого пользователя. 
 
👩🏻‍💻 Количество рефералов: *{len(referral['children'])}*
🤑 Ежедневное автопополнение: *{referral['award']}* `energy` ⚡

🎉 Ваша реферальная ссылка: `{referral_link}`
""")
