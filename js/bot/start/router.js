import { StartWithQuery, TextCommand } from '../filters.js';
import { helpText, helpCommand, appCommand } from '../commands.js';
import { checkSubscription } from '../gpt/utils.js';
import { createMainKeyboard, sendMessage } from '../main_keyboard.js';
import { tokenizeService, referralsService } from '../../services/index.js';

// import { Router } from 'grammy';
import { Router } from '../grammy_stub.js';
import { InlineKeyboard } from '../grammy_stub.js';

// --- Original aiogram imports (commented out for reference) ---
// import { Router as AiogramRouter } from 'aiogram';
// import { CommandStart } from 'aiogram/filters.js';
// import { Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup } from 'aiogram/types.js';
// --------------------------------------------------------------

// Temporary lightweight stubs to keep existing code functional during migration.
// They replicate only the minimal interface currently used in this file.
const CommandStart = (...args) => {
  return (ctx) => {
    const text = ctx?.message?.text ?? '';
    return text.startsWith('/start');
  };
};
// GrammY uses regular objects for messages/callbacks, so we leave Message/CallbackQuery
// as aliases to plain objects to satisfy any type assumptions.
const Message = Object;
const CallbackQuery = Object;
// Inline keyboard helpers compatible with grammY
class InlineKeyboardButton {
  constructor({ text, url, callback_data }) {
    this.text = text;
    if (url) this.url = url;
    if (callback_data) this.callback_data = callback_data;
  }
}
class InlineKeyboardMarkup {
  constructor({ inline_keyboard }) {
    this.reply_markup = new InlineKeyboard(inline_keyboard.flat());
  }
}

export const startRouter = new Router();

const helloText = `👋 Привет! Я бот от разработчиков deep.foundation!

🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение или нажми кнопку в меню!

/help - ✨ обзор команд и возможностей
/balance - ⚡️ узнать свой баланс
/referral - 🔗 подробности рефералки

Всё бесплатно, если не платить.
Каждый день твой баланс будет пополняться на сумму от *10 000⚡️* (энергии)!

Если нужно больше:
💎 Можно пополнить баланс Telegram звёздами или банковской картой.
👥 Понравилось? Поделись с друзьями и получи бонус за каждого приглашенного друга! Приводя много друзей ты сможешь пользоваться нейросетями практически безлимитно.

/referral - получай больше с реферальной системой:
*5 000⚡️️* за каждого приглашенного пользователя;
*+500⚡️️* к ежедневному пополнению баланса за каждого друга.

🏠 Если что-то пошло не так или хочешь поделиться вдохновением, напиши в наше сообщество @deepGPT.`;

const refText = `👋 Ты прибыл по реферальной ссылке, чтобы получить награду нужно подписаться на мой канал.`;

async function handleReferral(message, userId, refUserId) {
  const result = await referralsService.createReferral(userId, refUserId);
  console.log(result, 'resuuuuult');
  if (!refUserId) return;
  if (!result || result.parent == null) return;

  let chatId;
  try { chatId = parseInt(refUserId, 10); } catch { chatId = null; }
  if (!chatId) {
    await message.answer('❌ Некорректный реферальный ID.');
    return;
  }

  await message.answer(`🎉 Вы получили *5 000*⚡️!\n\n/balance - ✨ Узнать баланс\n/referral - 🔗 Подробности рефералки`);

  await message.bot.sendMessage(chatId, `🎉 Добавлен новый реферал! \nВы получили *5 000*⚡️!\nВаш реферал должен проявить любую активность в боте через 24 часа, чтобы вы получили еще *5 000*⚡️ и +500⚡️️ к ежедневному пополнению баланса.\n\n/balance - ✨ Узнать баланс\n/referral - 🔗 Подробности рефералки`);
}

async function createTokenIfNotExist(userId) {
  return await tokenizeService.get_tokens(userId);
}

startRouter.message(CommandStart(), async (message) => {
  const match = message.text.match(/^\/start\s(\S+)/);
  const refUserId = match ? match[1] : null;

  const keyboard = createMainKeyboard();
  await sendMessage(message, { text: helloText, reply_markup: keyboard });

  await createTokenIfNotExist(message.from_user.id);
  const isSubscribe = await checkSubscription(message);

  if (refUserId) {
    let chatId = null;
    try { chatId = parseInt(refUserId, 10); } catch {}
    if (chatId) {
      const userName = message.from_user.username;
      const fullName = message.from_user.full_name;
      const mention = `<a href='tg://user?id=${message.from_user.id}'>${fullName}</a>`;
      await message.bot.sendMessage(chatId, `🎉 По вашей реферальной ссылке перешли: @${userName} (${mention}).\n\nЧтобы вашему другу стать вашим рефералом, он должен подписаться на канал @gptDeep.\n\nКак только это произойдёт вы получите <b>5 000</b>⚡️ единоразово и <b>+500</b>⚡️️ к ежедневному пополнению баланса.\n\nЕсли вдруг этого долго не происходит, то возможно вашему другу нужна помощь, <b>попробуйте написать ему в личные сообщения</b>.\nЕсли и это не помогает, то обратитесь в поддержку в сообществе @deepGPT и мы поможем вам разобраться с ситуацией.`, { parse_mode: 'HTML' });
    }
  }

  if (!isSubscribe) {
    if (String(refUserId) !== String(message.from_user.id)) {
      await message.answer(refText, { reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
        new InlineKeyboardButton({ text: 'Подписаться 👊🏻', url: 'https://t.me/gptDeep' })
      ], [
        new InlineKeyboardButton({ text: 'Проверить ✅', callback_data: `ref-is-subscribe ${refUserId} ${message.from_user.id}` })
      ]] }) });
    }
    return;
  }

  await handleReferral(message, message.from_user.id, refUserId);
});

startRouter.callbackQuery(StartWithQuery('ref-is-subscribe'), async (callbackQuery) => {
  const [_, refUserId, userId] = callbackQuery.data.split(' ');
  const isSubscribe = await checkSubscription(callbackQuery.message, userId);
  if (!isSubscribe) {
    await callbackQuery.message.answer('Вы не подписались! 😡');
    return;
  }
  await handleReferral(callbackQuery.message, userId, refUserId);
});

startRouter.message(TextCommand([helpCommand(), helpText()]), async (message) => {
  await message.answer(`Основной ресурc для доступа к нейросетям - ⚡️ (энергия).\nЭто универсальный ресурс для всего функционала бота.\n\nКаждая нейросеть тратит разное количество ⚡️.\nКоличество затраченных ⚡️ зависит от длины истории диалога, моделей нейросетей и объёма ваших вопросов и ответов от нейросети.\nДля экономии используйте команду - /clear, чтобы не переполнять историю диалога и не увеличивать расход ⚡️ (энергии)! \nРекомендуется очищать контекст перед началом обсуждения новой темы. А также если выбранная модель начала отказывать в помощи.\n\n/app - 🔥 Получить ссылку к приложению!\n/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.\n/model - 🛠️ Сменить модель, перезапускает бот, позволяет сменить модель бота.\n/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить режим взаимодействия с ботом.   \n/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.  \n/balance - ✨ Баланс, позволяет узнать баланс ⚡️.\n/image - 🖼️ Генерация картинки (Midjourney, DALL·E 3, Flux, Stable Diffusion)\n/buy - 💎 Пополнить баланс, позволяет пополнить баланс ⚡️.\n/referral - 🔗 Получить реферальную ссылку\n/suno - 🎵 Генерация музыки (Suno)\n/text - Отправить текстовое сообщение`);
});

startRouter.message(TextCommand([appCommand()]), async (message) => {
  await message.answer('Ссылка на приложение: https://t.me/DeepGPTBot/App');
});
