import { Composer } from 'grammy';
import { tokenizeService, referralsService } from '../../services/index.js';
import { createLogger } from '../../utils/logger.js';
import { config } from '../../config.js';
import { sendMessage } from '../main_keyboard.js';

const logger = createLogger('balance_router');

export const balanceRouter = new Composer();



function formatBalanceMessage(ctx, { referral, gptTokens, getDateLine, acceptAccount }) {
  return ctx.t('balance.message', {
    referrals: referral.children.length,
    award: referral.award,
    accountStatus: acceptAccount(),
    dateLine: getDateLine(),
    tokens: gptTokens.tokens || 0
  });
}

async function sendBalance(ctx) {
  const userId = ctx.from.id;
  logger.debug('Balance requested for user:', userId);
  try {
    const gptTokens = await tokenizeService.get_tokens(userId);
    const referral = await referralsService.getReferral(userId);
    const lastUpdate = new Date(referral.lastUpdate);
    const newDate = new Date(lastUpdate.getTime() + 24 * 60 * 60 * 1000);
    const currentDate = new Date();

    function getDate() {
      if (newDate.getDate() === currentDate.getDate()) {
        return ctx.t('balance.today', { time: `${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}` });
      } else {
        return ctx.t('balance.tomorrow', { time: `${newDate.getHours()}:${String(newDate.getMinutes()).padStart(2, '0')}` });
      }
    }
    function getDateLine() {
      if ((gptTokens.tokens || 0) >= 30000) {
        return ctx.t('balance.autorefill_available');
      }
      return ctx.t('balance.next_autorefill', { date: getDate() });
    }
    function acceptAccount() {
      return referral.isActivated
        ? ctx.t('balance.account_confirmed')
        : ctx.t('balance.account_not_confirmed');
    }
    // Use sendMessage which handles MarkdownV2 properly
    const text = formatBalanceMessage(ctx, { referral, gptTokens, getDateLine, acceptAccount });
    await sendMessage(ctx, text);
  } catch (error) {
    logger.error('Error in balance command:', error);
    console.error('Full error details:', error);
    await sendMessage(ctx, ctx.t('balance.error'));
    if (config.isDev) process.exit(1);
  }
}

balanceRouter.command('balance', sendBalance);
balanceRouter.hears(['✨ Balance', '✨ Баланс'], sendBalance); 