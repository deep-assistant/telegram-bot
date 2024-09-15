from aiogram import BaseMiddleware
from aiogram.types import Message

from services import referralsService


class MiddlewareAward(BaseMiddleware):
    async def __call__(self, handler, event, data):
        reward = await referralsService.get_awards(event.from_user.id)

        print(reward)

        if reward["isAward"]:
            update_parents = reward["updateParents"]

            if len(update_parents) > 0:
                await event.bot.send_message(chat_id=event.from_user.id, text="""
🎉 Ваш аккаунт был подтвержден! 
Пользователь, который пригласил вас получил *+500* `energy`⚡ к ежедневному бесплатному пополнению!

/balance - ✨ Узнать баланс
/referral - 🔗 Приглашайте друзей - получайте больше бонусов!
""")


            for parent in update_parents:
                await event.bot.send_message(chat_id=parent, text="""
🎉 Ваш реферал был подтвержден! 
Вы получили *10000* `energy`⚡ 
М *+500* `energy`⚡ к ежедневному бесплатному пополнению!

/balance - ✨ Узнать баланс
/referral - 🔗 Подробности рефералки
""")

        return await handler(event, data)
