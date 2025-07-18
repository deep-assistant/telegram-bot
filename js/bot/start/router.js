import { helpText, helpCommand, appCommand } from '../commands.js';
import { checkSubscription } from '../gpt/utils.js';
import { createMainKeyboard, sendMessage } from '../main_keyboard.js';
import { tokenizeService, referralsService } from '../../services/index.js';

import { Composer, InlineKeyboard } from 'grammy';
import createDebug from 'debug';
const debug = createDebug('telegram-bot:start_router');

// Greeting text moved to locales/en.yml & ru.yml under key "start.greeting"

const refText = `👋 Ты прибыл по реферальной ссылке, чтобы получить награду нужно подписаться на мой канал.`;

async function handleReferral(ctx, userId, refUserId) {
  const result = await referralsService.createReferral(userId, refUserId);
  console.log(result, 'resuuuuult');
  if (!refUserId) return;
  if (!result || result.parent == null) return;

  let chatId;
  try { chatId = parseInt(refUserId, 10); } catch { chatId = null; }
  if (!chatId) {
    await sendMessage(ctx, '❌ Некорректный реферальный ID.');
    return;
  }

  await sendMessage(ctx, `🎉 Вы получили *5 000*⚡️!\n\n/balance - ✨ Узнать баланс\n/referral - 🔗 Подробности рефералки`);

  await ctx.api.sendMessage(chatId, `🎉 Добавлен новый реферал! \nВы получили *5 000*⚡️!\nВаш реферал должен проявить любую активность в боте через 24 часа, чтобы вы получили еще *5 000*⚡️ и +500⚡️️ к ежедневному пополнению баланса.\n\n/balance - ✨ Узнать баланс\n/referral - 🔗 Подробности рефералки`);
}

async function createTokenIfNotExist(userId) {
  return await tokenizeService.get_tokens(userId);
}

export const startRouter = new Composer();

startRouter.command('start', async (ctx) => {
  debug('Start command handler triggered');
  const refUserId = ctx.match;

  const keyboard = createMainKeyboard();
  const greeting = ctx.t ? ctx.t('start.greeting') : 'Привет!';
  await sendMessage(ctx, { text: greeting, reply_markup: keyboard });

  await createTokenIfNotExist(ctx.from.id);
  const isSubscribe = await checkSubscription(ctx);

  if (refUserId) {
    let chatId = null;
    try { chatId = parseInt(refUserId, 10); } catch {}
    if (chatId) {
      const userName = ctx.from.username;
      const fullName = ctx.from.first_name + (ctx.from.last_name ? ' ' + ctx.from.last_name : '');
      const mention = `<a href='tg://user?id=${ctx.from.id}'>${fullName}</a>`;
      await ctx.api.sendMessage(chatId, `🎉 По вашей реферальной ссылке перешли: @${userName} (${mention}).\n\nЧтобы вашему другу стать вашим рефералом, он должен подписаться на канал @gptDeep.\n\nКак только это произойдёт вы получите <b>5 000</b>⚡️ единоразово и <b>+500</b>⚡️️ к ежедневному пополнению баланса.\n\nЕсли вдруг этого долго не происходит, то возможно вашему другу нужна помощь, <b>попробуйте написать ему в личные сообщения</b>.\nЕсли и это не помогает, то обратитесь в поддержку в сообществе @deepGPT и мы поможем вам разобраться с ситуацией.`, { parse_mode: 'HTML' });
    }
  }

  if (!isSubscribe) {
    if (String(refUserId) !== String(ctx.from.id)) {
      const inlineKb = new InlineKeyboard()
        .url('Подписаться 👊🏻', 'https://t.me/gptDeep').row()
        .text('Проверить ✅', `ref-is-subscribe ${refUserId} ${ctx.from.id}`);
      await sendMessage(ctx, refText, { reply_markup: inlineKb });
    }
    return;
  }

  await handleReferral(ctx, ctx.from.id, refUserId);
});

startRouter.callbackQuery(/ref-is-subscribe (\S+) (\S+)/, async (ctx) => {
  const refUserId = ctx.match[1];
  const userId = ctx.match[2];
  const isSubscribe = await checkSubscription(ctx.message, userId);
  if (!isSubscribe) {
    await sendMessage(ctx, 'Вы не подписались! 😡');
    return;
  }
  await handleReferral(ctx, userId, refUserId);
});

startRouter.hears([helpCommand(), helpText()], async (ctx) => {
  await sendMessage(ctx, `Основной ресурc для доступа к нейросетей - ⚡️ (энергия).\nЭто универсальный ресурс для всего функционала бота.\n\nКаждая нейросеть тратит разное количество ⚡️.\nКоличество затраченных ⚡️ зависит от длины истории диалога, моделей нейросетей и объёма ваших вопросов и ответов от нейросети.\nДля экономии используйте команду - /clear, чтобы не переполнять историю диалога и не увеличивать расход ⚡️ (энергии)! \nРекомендуется очищать контекст перед началом обсуждения новой темы. А также если выбранная модель начала отказывать в помощи.\n\n/app - 🔥 Получить ссылку к приложению!\n/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.\n/model - 🛠️ Сменить модель, перезапускает бот, позволяет сменить модель бота.\n/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить режим взаимодействия с ботом.   \n/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.  \n/balance - ✨ Баланс, позволяет узнать баланс ⚡️.\n/image - 🖼️ Генерация картинки (Midjourney, DALL·E 3, Flux, Stable Diffusion)\n/buy - 💎 Пополнить баланс, позволяет пополнить баланс ⚡️.\n/referral - 🔗 Получить реферальную ссылку\n/suno - 🎵 Генерация музыки (Suno)\n/text - Отправить текстовое сообщение`);
});

startRouter.hears(appCommand(), async (ctx) => {
  await sendMessage(ctx, 'Ссылка на приложение: https://t.me/DeepGPTBot/App');
});
