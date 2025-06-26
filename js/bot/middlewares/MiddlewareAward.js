import { BaseMiddleware } from 'aiogram';
import { referralsService } from '../../services/referrals_service.js';

// Middleware to send referral award notifications
export class MiddlewareAward extends BaseMiddleware {
  async __call__(handler, event, data) {
    // Get referral awards for user
    const reward = await referralsService.getAwards(event.from_user.id);
    console.log('Referral reward:', reward);

    // If an award was granted, notify user and their referrers
    if (reward.isAward) {
      const updateParents = reward.updateParents || [];

      // Notify the user who just got awarded
      if (updateParents.length > 0) {
        await event.bot.sendMessage(event.from_user.id,
          `🎉 Ваш аккаунт был подтвержден! 
Пользователь, который пригласил вас получил *10000⚡️* и *+500⚡️* к ежедневному бесплатному пополнению!

/balance - ✨ Узнать баланс
/referral - 🔗 Приглашайте друзей - получайте больше бонусов!`,
          { parse_mode: 'Markdown' }
        );
      }

      // Notify each parent who referred this user
      for (const parentId of updateParents) {
        await event.bot.sendMessage(parentId,
          `🎉 Ваш реферал был подтвержден! 
Вы получили *10000⚡️* 
И *+500⚡️* к ежедневному бесплатному пополнению!

/balance - ✨ Узнать баланс
/referral - 🔗 Подробности рефералки`,
          { parse_mode: 'Markdown' }
        );
      }
    }

    // Continue with next handler
    return handler(event, data);
  }
}
