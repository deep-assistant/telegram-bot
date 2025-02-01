import logging

from aiogram import Router, types

from bot.filters import TextCommand
from bot.referral.command_types import referral_command, referral_command_text
from bot.constants import DEFAULT_ERROR_MESSAGE
from services import referralsService

referralRouter = Router()


@referralRouter.message(TextCommand([referral_command(), referral_command_text()]))
async def handle_start_referral_generation(message: types.Message):
    try:
        bot_info = await message.bot.get_me()
        user_id = message.from_user.id
        referral_link = f"https://t.me/{bot_info.username}?start={user_id}"

        logging.info(f"Пользователь {user_id} запросил реферальную ссылку.")

        await message.bot.send_chat_action(message.chat.id, "typing")
        referral = await referralsService.get_referral(user_id)

        if not referral:
            await message.answer("Реферальная система недоступна.")
            return

        response_text = f"""
*15 000*⚡️ за каждого приглашенного пользователя. 
*+500*⚡️ к ежедневному пополнению баланса за каждого пользователя. 

👩🏻‍💻 Количество рефералов: *{len(referral['children'])}*
🤑 Ежедневное автопополнение: *{referral['award']}*⚡️

🎉 Ваша реферальная ссылка: `{referral_link}`
        """
        await message.answer(response_text)

    except Exception as e:
        logging.error(f"Ошибка в реферальной системе: {e}")
        await message.answer(DEFAULT_ERROR_MESSAGE)
        
