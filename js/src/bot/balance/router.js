import { Composer } from 'grammy';
import { createLogger } from '../../utils/logger.js';
import { tokenizeService, referralsService } from '../../services/index.js';
import { config } from '../../config.js';
import { sendMessage } from '../main_keyboard.js';

const log = createLogger('balance_router');

export const balanceRouter = new Composer();

function formatBalanceMessage(ctx, { referral, gptTokens, getDateLine, acceptAccount }) {
  const tokens = gptTokens?.tokens || 0;
  return ctx.t('balance.message', {
    referrals: referral.children.length,
    award: referral.award,
    accountStatus: acceptAccount(),
    dateLine: getDateLine(),
    tokens: tokens
  });
}

async function sendBalance(ctx) {
  const userId = ctx.from.id;
  log.debug('Balance requested for user:', userId);
  try {
    const gptTokens = await tokenizeService.get_tokens(userId);
    log.debug('gptTokens received:', gptTokens);
    const referral = await referralsService.getReferral(userId);
    log.debug('referral received:', referral);
    
    if (!gptTokens) {
      log.error('Failed to get gptTokens for user:', userId);
      await sendMessage(ctx, ctx.t('balance.error'));
      return;
    }
    
    if (!referral) {
      log.error('Failed to get referral for user:', userId);
      await sendMessage(ctx, ctx.t('balance.error'));
      return;
    }
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
    log.error('Error in balance command:', () => error);
    console.error('Full error details:', error);
    await sendMessage(ctx, ctx.t('balance.error'));
    if (config.isDev) process.exit(1);
  }
}

balanceRouter.command('balance', sendBalance);
balanceRouter.hears(['✨ Balance', '✨ Баланс'], sendBalance); 