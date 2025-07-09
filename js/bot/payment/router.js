import { Router } from 'aiogram';
import { InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice } from 'aiogram/types.js';
import { TextCommand, StartWithQuery } from '../filters.js';
import {
  PAYMENT_COMMAND_START,
  PAYMENT_COMMAND_TEXT,
  BALANCE_PAYMENT_COMMAND_TEXT,
  BALANCE_PAYMENT_COMMAND_START
} from '../commands.js';
import config from '../../config.js';
import { donationProduct, buyBalanceProduct } from './products.js';
import { GPTModels, tokenizeService } from '../../services/index.js';

export const paymentsRouter = new Router();

const donationText = `Благодарим за поддержку проекта! 🤩    
Скоро мы будем радовать вас новым и крутым функционалом!

Выбери сумму пожертвования:`;

// кнопки для выбора суммы пожертвования
const donationButtons = [
  [
    new InlineKeyboardButton({ text: '10 RUB', callback_data: 'donation 10' }),
    new InlineKeyboardButton({ text: '50 RUB', callback_data: 'donation 50' }),
    new InlineKeyboardButton({ text: '100 RUB', callback_data: 'donation 100' }),
  ],
  [
    new InlineKeyboardButton({ text: '150 RUB', callback_data: 'donation 150' }),
    new InlineKeyboardButton({ text: '250 RUB', callback_data: 'donation 250' }),
    new InlineKeyboardButton({ text: '500 RUB', callback_data: 'donation 500' }),
  ]
];

function paymentKeyboard(amount) {
  return new InlineKeyboardMarkup({ inline_keyboard: [[
    new InlineKeyboardButton({ text: `Оплатить ${amount} ⭐️`, pay: true })
  ]] });
}

function createBuyBalanceKeyboardModel() {
  return new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [[
      new InlineKeyboardButton({ text: '🤖 GPT-4o', callback_data: `buy-gpt ${GPTModels.GPT_4o}` }),
      new InlineKeyboardButton({ text: '🦾 GPT-3.5', callback_data: `buy-gpt ${GPTModels.GPT_3_5}` }),
    ]]
  });
}

function createBuyBalanceKeyboardMethod(model) {
  return new InlineKeyboardMarkup({
    resize_keyboard: true,
    inline_keyboard: [[
      new InlineKeyboardButton({ text: 'Telegram Stars ⭐️', callback_data: `buy_method_stars ${model} stars` }),
      new InlineKeyboardButton({ text: 'Оплата картой 💳', callback_data: `buy_method_card ${model} card` }),
    ]]
  });
}

// /donut и /donation команды
paymentsRouter.message(
  TextCommand([PAYMENT_COMMAND_START, PAYMENT_COMMAND_TEXT]),
  async (message) => {
    await message.answer(donationText, {
      reply_markup: new InlineKeyboardMarkup({
        resize_keyboard: true,
        inline_keyboard: donationButtons
      })
    });
  }
);

// /buy команды
paymentsRouter.message(
  TextCommand([BALANCE_PAYMENT_COMMAND_TEXT, BALANCE_PAYMENT_COMMAND_START]),
  async (message) => {
    // по умолчанию пополнение для GPT-4o
    await message.answer('Выберите модель для пополнения баланса', {
      reply_markup: createBuyBalanceKeyboardModel()
    });
  }
);

// Назад к выбору модели
paymentsRouter.callbackQuery(
  StartWithQuery('back_buy_model'),
  async (callbackQuery) => {
    try {
      await callbackQuery.message.edit_text('Баланс какой модели вы хотите пополнить?');
      await callbackQuery.message.edit_reply_markup({ reply_markup: createBuyBalanceKeyboardModel() });
    } catch {}
  }
);

// Назад к выбору способа оплаты
paymentsRouter.callbackQuery(
  StartWithQuery('back_buy_method'),
  async (callbackQuery) => {
    const model = callbackQuery.data.split(' ')[1];
    try {
      await callbackQuery.message.edit_text('Выберите способ оплаты');
      await callbackQuery.message.edit_reply_markup({ reply_markup: createBuyBalanceKeyboardMethod(model) });
    } catch {}
  }
);

// Выбор Telegram Stars
paymentsRouter.callbackQuery(
  StartWithQuery('buy_method_stars'),
  async (callbackQuery) => {
    const model = callbackQuery.data.split(' ')[1];
    await callbackQuery.message.edit_text('Насколько ⚡️ вы хотите пополнить баланс?');
    // примеры: токены
    const prices = [25000, 50000, 100000, 250000, 500000, 1000000];
    const buttons = prices.map(p => [
      new InlineKeyboardButton({ text: `${p.toLocaleString()}⚡️`, callback_data: `buy_stars ${p} ${model}` })
    ]);
    buttons.push([
      new InlineKeyboardButton({ text: '⬅️ Назад к выбору способа оплаты', callback_data: `back_buy_method ${model}` })
    ]);
    await callbackQuery.message.edit_reply_markup({ reply_markup: new InlineKeyboardMarkup({ inline_keyboard: buttons }) });
  }
);

// Выбор оплаты картой
paymentsRouter.callbackQuery(
  StartWithQuery('buy_method_card'),
  async (callbackQuery) => {
    const model = callbackQuery.data.split(' ')[1];
    await callbackQuery.message.edit_text('Насколько ⚡️ вы хотите пополнить баланс?');
    const prices = [100000, 250000, 500000, 1000000, 2500000, 5000000];
    const buttons = prices.map(p => [
      new InlineKeyboardButton({ text: `${p.toLocaleString()}⚡️`, callback_data: `buy_card ${p} ${model}` })
    ]);
    buttons.push([
      new InlineKeyboardButton({ text: '⬅️ Назад к выбору способа оплаты', callback_data: `back_buy_method ${model}` })
    ]);
    await callbackQuery.message.edit_reply_markup({ reply_markup: new InlineKeyboardMarkup({ inline_keyboard: buttons }) });
  }
);

// Отправка invoice для Stars
paymentsRouter.callbackQuery(
  StartWithQuery('buy_stars'),
  async (callbackQuery) => {
    const tokens = callbackQuery.data.split(' ')[1];
    const model = callbackQuery.data.split(' ')[2];
    const amount = parseInt(tokens, 10);
    await callbackQuery.message.answer_invoice({
      title: 'Покупка ⚡️',
      description: `Купить ${tokens}⚡️?`,
      payload: `buy_balance ${tokens} ${model} stars`,
      provider_token: config.PAYMENTS_TOKEN,
      currency: 'XTR',
      prices: [ new LabeledPrice({ label: 'XTR', amount }) ]
    });
    await new Promise(r => setTimeout(r, 500));
    await callbackQuery.message.delete();
  }
);

// Отправка invoice для карты
paymentsRouter.callbackQuery(
  StartWithQuery('buy_card'),
  async (callbackQuery) => {
    const tokens = callbackQuery.data.split(' ')[1];
    const model = callbackQuery.data.split(' ')[2];
    const amount = parseInt(tokens, 10) * 100;
    await callbackQuery.message.bot.send_invoice(
      callbackQuery.message.chat.id,
      { ...buyBalanceProduct,
        description: `🤩 Покупка ${tokens}⚡️`,
        payload: `buy_balance ${tokens} ${model} card`,
        prices: [ new LabeledPrice({ label: `Покупка ${tokens}⚡️`, amount }) ]
      }
    );
    await new Promise(r => setTimeout(r, 500));
    await callbackQuery.message.delete();
  }
);

// Обработка donation
paymentsRouter.callbackQuery(
  StartWithQuery('donation'),
  async (callbackQuery) => {
    const amount = parseInt(callbackQuery.data.split(' ')[1], 10) * 100;
    await callbackQuery.message.bot.send_invoice(
      callbackQuery.message.chat.id,
      { ...donationProduct,
        prices: [ new LabeledPrice({ label: 'Пожертвование', amount }) ]
      }
    );
    await new Promise(r => setTimeout(r, 500));
    await callbackQuery.message.delete();
  }
);

// Pre-checkout
paymentsRouter.preCheckoutQuery((query) => true, async (preCheckoutQuery) => {
  await preCheckoutQuery.answerPreCheckoutQuery({ ok: true });
});

// Успешная оплата
paymentsRouter.message(
  (message) => Boolean(message.successful_payment),
  async (message) => {
    const { successful_payment } = message;
    if (successful_payment.invoice_payload.startsWith('donation')) {
      const sum = successful_payment.total_amount / 100;
      await message.answer(`🤩 Платёж на сумму *${sum} ${successful_payment.currency}* прошел успешно! 🤩\n\nБлагодарим за поддержку проекта!`);
    } else if (successful_payment.invoice_payload.startsWith('buy_balance')) {
      const parts = successful_payment.invoice_payload.split(' ');
      const tokens = parseInt(parts[1], 10);
      await tokenizeService.update_user_token(message.from_user.id, tokens, 'add');
      await message.answer(`🤩 Ваш баланс пополнен на *${tokens}*⚡️!`);
      const { tokens: newTokens } = await tokenizeService.get_tokens(message.from_user.id);
      await message.answer(`💵 Текущий баланс: *${newTokens}⚡️*`);
    }
  }
);
