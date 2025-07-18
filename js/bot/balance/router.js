import { Composer } from 'grammy';
import { tokenizeService, referralsService } from '../../services/index.js';
import { createLogger } from '../../utils/logger.js';
import { config } from '../../config.js';

const logger = createLogger('balance_router');

export const balanceRouter = new Composer();

// Balance command handler
balanceRouter.command('balance', async (ctx) => {
  const userId = ctx.from.id;
  logger.debug('Balance command triggered for user:', userId);
  
  try {
    // Fetch token and referral info
    const gptTokens = await tokenizeService.get_tokens(userId);
    const referral = await referralsService.getReferral(userId);

    // Calculate next refill time
    const lastUpdate = new Date(referral.lastUpdate);
    const newDate = new Date(lastUpdate.getTime() + 24 * 60 * 60 * 1000);
    const currentDate = new Date();

    function getDate() {
      if (newDate.getDate() === currentDate.getDate()) {
        return `Сегодня в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
      } else {
        return `Завтра в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
      }
    }

    function getDateLine() {
      if ((gptTokens.tokens || 0) >= 30000) {
        return '🕒 Автопополнение доступно, если меньше *30000*⚡️';
      }
      return `🕒 Следующее автопополнение будет: *${getDate()}*`;
    }

    function acceptAccount() {
      return referral.isActivated
        ? '🔑 Ваш аккаунт подтвержден!'
        : '🔑 Ваш аккаунт не подтвержден, зайдите через сутки и совершите любое действие!';
    }

    // Send balance info
    await ctx.reply(`👩🏻‍💻 Количество рефералов: *${referral.children.length}*
🤑 Ежедневное автопополнение 🔋: *${referral.award}⚡️*
${acceptAccount()}

${getDateLine()}

💵 Текущий баланс: *${gptTokens.tokens || 0}⚡️*`);
  } catch (error) {
    logger.error('Error in balance command:', error);
    console.error('Full error details:', error);
    await ctx.reply('Ошибка при получении баланса. Попробуйте позже.');
    if (config.isDev) process.exit(1);
  }
});

// Balance button handler (English)
balanceRouter.hears('✨ Balance', async (ctx) => {
  const userId = ctx.from.id;
  logger.debug('Balance button triggered for user:', userId);
  
  try {
    // Fetch token and referral info
    const gptTokens = await tokenizeService.get_tokens(userId);
    const referral = await referralsService.getReferral(userId);

    // Calculate next refill time
    const lastUpdate = new Date(referral.lastUpdate);
    const newDate = new Date(lastUpdate.getTime() + 24 * 60 * 60 * 1000);
    const currentDate = new Date();

    function getDate() {
      if (newDate.getDate() === currentDate.getDate()) {
        return `Сегодня в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
      } else {
        return `Завтра в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
      }
    }

    function getDateLine() {
      if ((gptTokens.tokens || 0) >= 30000) {
        return '🕒 Автопополнение доступно, если меньше *30000*⚡️';
      }
      return `🕒 Следующее автопополнение будет: *${getDate()}*`;
    }

    function acceptAccount() {
      return referral.isActivated
        ? '🔑 Ваш аккаунт подтвержден!'
        : '🔑 Ваш аккаунт не подтвержден, зайдите через сутки и совершите любое действие!';
    }

    // Send balance info
    await ctx.reply(`👩🏻‍💻 Количество рефералов: *${referral.children.length}*
🤑 Ежедневное автопополнение 🔋: *${referral.award}⚡️*
${acceptAccount()}

${getDateLine()}

💵 Текущий баланс: *${gptTokens.tokens || 0}⚡️*`);
  } catch (error) {
    logger.error('Error in balance button:', error);
    console.error('Full error details:', error);
    await ctx.reply('Ошибка при получении баланса. Попробуйте позже.');
    if (config.isDev) process.exit(1);
  }
});

// Balance button handler (Russian)
balanceRouter.hears('✨ Баланс', async (ctx) => {
  const userId = ctx.from.id;
  logger.debug('Balance button (Russian) triggered for user:', userId);
  
  try {
    // Fetch token and referral info
    const gptTokens = await tokenizeService.get_tokens(userId);
    const referral = await referralsService.getReferral(userId);

    // Calculate next refill time
    const lastUpdate = new Date(referral.lastUpdate);
    const newDate = new Date(lastUpdate.getTime() + 24 * 60 * 60 * 1000);
    const currentDate = new Date();

    function getDate() {
      if (newDate.getDate() === currentDate.getDate()) {
        return `Сегодня в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
      } else {
        return `Завтра в ${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}`;
      }
    }

    function getDateLine() {
      if ((gptTokens.tokens || 0) >= 30000) {
        return '🕒 Автопополнение доступно, если меньше *30000*⚡️';
      }
      return `🕒 Следующее автопополнение будет: *${getDate()}*`;
    }

    function acceptAccount() {
      return referral.isActivated
        ? '🔑 Ваш аккаунт подтвержден!'
        : '🔑 Ваш аккаунт не подтвержден, зайдите через сутки и совершите любое действие!';
    }

    // Send balance info
    await ctx.reply(`👩🏻‍💻 Количество рефералов: *${referral.children.length}*
🤑 Ежедневное автопополнение 🔋: *${referral.award}⚡️*
${acceptAccount()}

${getDateLine()}

💵 Текущий баланс: *${gptTokens.tokens || 0}⚡️*`);
  } catch (error) {
    logger.error('Error in balance button (Russian):', error);
    console.error('Full error details:', error);
    await ctx.reply('Ошибка при получении баланса. Попробуйте позже.');
    if (config.isDev) process.exit(1);
  }
}); 