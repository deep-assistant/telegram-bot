import { helpText, helpCommand, appCommand } from '../commands.js';
import { checkSubscription } from '../gpt/utils.js';
import { createMainKeyboard, sendMessage } from '../main_keyboard.js';
import { tokenizeService, referralsService } from '../../services/index.js';
import { createLogger, lazyDebug } from '../../utils/logger.js';

import { Composer, InlineKeyboard } from 'grammy';

const logger = createLogger('start_router');

// Greeting text moved to locales/en.yml & ru.yml under key "start.greeting"

async function handleReferral(ctx, userId, refUserId) {
  const result = await referralsService.createReferral(userId, refUserId);
  logger.debug('Referral result:', result);
  if (!refUserId) return;
  if (!result || result.parent == null) return;

  let chatId;
  try { chatId = parseInt(refUserId, 10); } catch { chatId = null; }
  if (!chatId) {
    await sendMessage(ctx, ctx.t('start.invalid_ref_id'));
    return;
  }

  await sendMessage(ctx, ctx.t('start.referral_bonus'));

  await ctx.api.sendMessage(chatId, ctx.t('start.new_referral'), { parse_mode: 'MarkdownV2' });
}

async function createTokenIfNotExist(userId) {
  return await tokenizeService.get_tokens(userId);
}

export const startRouter = new Composer();

startRouter.command('start', async (ctx) => {
  logger.trace(`Raw start command context: from=${JSON.stringify(ctx.from)}, chat=${JSON.stringify(ctx.chat)}, match=${ctx.match}`);
  logger.debug('Start command handler triggered');
  const refUserId = ctx.match;

  const keyboard = createMainKeyboard(ctx);
  const greeting = ctx.t ? ctx.t('start.greeting') : 'Привет!';
  await sendMessage(ctx, { text: greeting, reply_markup: keyboard });

  await createTokenIfNotExist(ctx.from.id);
  const isSubscribe = await checkSubscription(ctx);

  if (refUserId) {
    let chatId = null;
    try { chatId = parseInt(refUserId, 10); } catch {}
    if (chatId) {
      const userName = ctx.from.username || '';
      const fullName = `${ctx.from.first_name}${ctx.from.last_name ? ' ' + ctx.from.last_name : ''}`;
      const mention = `<a href='tg://user?id=${ctx.from.id}'>${fullName}</a>`;
      const refNotifyText = ctx.t('start.ref_notification', { username: userName ? `@${userName}` : fullName, mention });
      await ctx.api.sendMessage(chatId, refNotifyText, { parse_mode: 'HTML' });
    }
  }

  if (!isSubscribe) {
    if (String(refUserId) !== String(ctx.from.id)) {
      const inlineKb = new InlineKeyboard()
        .url(ctx.t('start.subscribe_button'), 'https://t.me/gptDeep').row()
        .text(ctx.t('start.check_button'), `ref-is-subscribe ${refUserId} ${ctx.from.id}`);
      await sendMessage(ctx, ctx.t('start.ref_text'), { reply_markup: inlineKb });
    }
    return;
  }

  await handleReferral(ctx, ctx.from.id, refUserId);
});

startRouter.callbackQuery(/ref-is-subscribe (\S+) (\S+)/, async (ctx) => {
  const refUserId = ctx.match[1];
  const userId = ctx.match[2];
  const isSubscribe = await checkSubscription(ctx, userId);
  if (!isSubscribe) {
    await sendMessage(ctx, ctx.t('start.not_subscribed'));
    return;
  }
  await handleReferral(ctx, userId, refUserId);
});

startRouter.hears([helpCommand(), helpText()], async (ctx) => {
  await sendMessage(ctx, ctx.t('start.help'));
});

startRouter.hears(appCommand(), async (ctx) => {
  await sendMessage(ctx, ctx.t('start.app_link'));
});


