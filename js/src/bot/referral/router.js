import { Router } from 'aiogram';
import { TextCommand } from '../filters.js';
import { referralCommand, referralCommandText } from '../commands.js';
import { DEFAULT_ERROR_MESSAGE } from '../constants.js';
import { referralsService } from '../../services/referrals_service.js';

export const referralRouter = new Router();

referralRouter.message(TextCommand([referralCommand, referralCommandText]), async (message) => {
  try {
    const botInfo = await message.bot.get_me();
    const userId = message.from_user.id;
    const referralLink = `https://t.me/${botInfo.username}?start=${userId}`;
    await message.bot.send_chat_action(message.chat.id, 'typing');

    const referral = await referralsService.getReferral(userId);
    if (!referral) {
      await message.answer('Реферальная система недоступна.');
      return;
    }

    const responseText = `**5 000**⚡️ за каждого приглашенного пользователя.
**+500**⚡️ к ежедневному пополнению баланса за каждого пользователя.

👩🏻‍💻 Количество рефералов: **${referral.children.length}**
🤑 Ежедневное автопополнение: **${referral.award}**⚡️

🎉 Ваша реферальная ссылка: \`${referralLink}\``;

    await message.answer(responseText);
  } catch (e) {
    await message.answer(DEFAULT_ERROR_MESSAGE);
    console.error('Failed to generate referral link:', e);
  }
});
