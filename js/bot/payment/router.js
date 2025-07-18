import { Composer, InlineKeyboard } from 'grammy';
import { TextCommand, StartWithQuery } from '../filters.js';
import {
  PAYMENT_COMMAND_START,
  PAYMENT_COMMAND_TEXT,
  BALANCE_PAYMENT_COMMAND_TEXT,
  BALANCE_PAYMENT_COMMAND_START
} from '../commands.js';
import { config } from '../../config.js';
import { donationProduct, buyBalanceProduct } from './products.js';
import { GPTModels, tokenizeService } from '../../services/index.js';
import { createLogger } from '../../utils/logger.js';

const logger = createLogger('payment_router');

export const paymentRouter = new Composer();

// Donation buttons
const donationButtons = [
  [
    new InlineKeyboard().text('10 RUB', 'donation 10'),
    new InlineKeyboard().text('50 RUB', 'donation 50'),
    new InlineKeyboard().text('100 RUB', 'donation 100'),
  ],
  [
    new InlineKeyboard().text('150 RUB', 'donation 150'),
    new InlineKeyboard().text('250 RUB', 'donation 250'),
    new InlineKeyboard().text('500 RUB', 'donation 500'),
  ]
];

function createBuyBalanceKeyboardModel() {
  return new InlineKeyboard()
    .text('🤖 GPT-4o', `buy-gpt ${GPTModels.GPT_4o}`)
    .text('🦾 GPT-3.5', `buy-gpt ${GPTModels.GPT_3_5}`)
    .row();
}

function createBuyBalanceKeyboardMethod(model) {
  return new InlineKeyboard()
    .text('Telegram Stars ⭐️', `buy_method_stars ${model} stars`)
    .text('Оплата картой 💳', `buy_method_card ${model} card`)
    .row();
}

// /donut and /donation commands
paymentRouter.command('donut', async (ctx) => {
  logger.debug('Donation command triggered');
  await ctx.reply(ctx.t('payment.donation.title') + '\n\n' + ctx.t('payment.donation.subtitle') + '\n\n' + ctx.t('payment.donation.choose_amount'), {
    reply_markup: new InlineKeyboard()
      .text('10 RUB', 'donation 10')
      .text('50 RUB', 'donation 50')
      .text('100 RUB', 'donation 100')
      .row()
      .text('150 RUB', 'donation 150')
      .text('250 RUB', 'donation 250')
      .text('500 RUB', 'donation 500')
      .row()
  });
});

paymentRouter.hears([PAYMENT_COMMAND_TEXT], async (ctx) => {
  logger.debug('Donation command triggered');
  await ctx.reply(ctx.t('payment.donation.title') + '\n\n' + ctx.t('payment.donation.subtitle') + '\n\n' + ctx.t('payment.donation.choose_amount'), {
    reply_markup: new InlineKeyboard()
      .text('10 RUB', 'donation 10')
      .text('50 RUB', 'donation 50')
      .text('100 RUB', 'donation 100')
      .row()
      .text('150 RUB', 'donation 150')
      .text('250 RUB', 'donation 250')
      .text('500 RUB', 'donation 500')
      .row()
  });
});

// /buy commands
paymentRouter.command('buy', async (ctx) => {
  logger.debug('Buy command triggered');
  await ctx.reply(ctx.t('payment.choose_model'), {
    reply_markup: createBuyBalanceKeyboardModel()
  });
});

paymentRouter.hears([BALANCE_PAYMENT_COMMAND_TEXT], async (ctx) => {
  logger.debug('Buy command triggered');
  await ctx.reply(ctx.t('payment.choose_model'), {
    reply_markup: createBuyBalanceKeyboardModel()
  });
});

// Back to model selection
paymentRouter.callbackQuery(
  StartWithQuery('back_buy_model'),
  async (ctx) => {
    try {
      await ctx.editMessageText(ctx.t('payment.choose_model'));
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardModel() });
    } catch (error) {
      logger.error('Error in back_buy_model:', error);
    }
  }
);

// Back to payment method selection
paymentRouter.callbackQuery(
  StartWithQuery('back_buy_method'),
  async (ctx) => {
    const model = ctx.callbackQuery.data.split(' ')[1];
    try {
      await ctx.editMessageText(ctx.t('payment.choose_payment_method'));
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardMethod(model) });
    } catch (error) {
      logger.error('Error in back_buy_method:', error);
    }
  }
);

// Telegram Stars selection
paymentRouter.callbackQuery(
  StartWithQuery('buy_method_stars'),
  async (ctx) => {
    const model = ctx.callbackQuery.data.split(' ')[1];
    await ctx.editMessageText(ctx.t('payment.how_much_energy'));
    
    const prices = [25000, 50000, 100000, 250000, 500000, 1000000];
    const keyboard = new InlineKeyboard();
    
    prices.forEach((price, index) => {
      keyboard.text(`${price.toLocaleString()}⚡️`, `buy_stars ${price} ${model}`);
      if (index % 2 === 1 || index === prices.length - 1) {
        keyboard.row();
      }
    });
    
    keyboard.text(ctx.t('payment.back_to_payment_method'), `back_buy_method ${model}`);
    
    await ctx.editMessageReplyMarkup({ reply_markup: keyboard });
  }
);

// Card payment selection
paymentRouter.callbackQuery(
  StartWithQuery('buy_method_card'),
  async (ctx) => {
    const model = ctx.callbackQuery.data.split(' ')[1];
    await ctx.editMessageText(ctx.t('payment.how_much_energy'));
    
    const prices = [100000, 250000, 500000, 1000000, 2500000, 5000000];
    const keyboard = new InlineKeyboard();
    
    prices.forEach((price, index) => {
      keyboard.text(`${price.toLocaleString()}⚡️`, `buy_card ${price} ${model}`);
      if (index % 2 === 1 || index === prices.length - 1) {
        keyboard.row();
      }
    });
    
    keyboard.text(ctx.t('payment.back_to_payment_method'), `back_buy_method ${model}`);
    
    await ctx.editMessageReplyMarkup({ reply_markup: keyboard });
  }
);

// Send invoice for Stars
paymentRouter.callbackQuery(
  StartWithQuery('buy_stars'),
  async (ctx) => {
    const tokens = ctx.callbackQuery.data.split(' ')[1];
    const model = ctx.callbackQuery.data.split(' ')[2];
    const amount = parseInt(tokens, 10);
    
    await ctx.api.sendInvoice(ctx.chat.id, {
      title: ctx.t('payment.purchase_energy'),
      description: ctx.t('payment.buy_energy_question', { tokens }),
      payload: `buy_balance ${tokens} ${model} stars`,
      provider_token: config.paymentsToken,
      currency: 'XTR',
      prices: [{ label: 'XTR', amount }]
    });
    
    await new Promise(r => setTimeout(r, 500));
    await ctx.deleteMessage();
  }
);

// Send invoice for card
paymentRouter.callbackQuery(
  StartWithQuery('buy_card'),
  async (ctx) => {
    const tokens = ctx.callbackQuery.data.split(' ')[1];
    const model = ctx.callbackQuery.data.split(' ')[2];
    const amount = parseInt(tokens, 10) * 100;
    
    await ctx.api.sendInvoice(ctx.chat.id, {
      ...buyBalanceProduct,
      description: ctx.t('payment.buy_energy_question', { tokens }),
      payload: `buy_balance ${tokens} ${model} card`,
      prices: [{ label: ctx.t('payment.buy_energy_question', { tokens }), amount }]
    });
    
    await new Promise(r => setTimeout(r, 500));
    await ctx.deleteMessage();
  }
);

// Handle donation
paymentRouter.callbackQuery(
  StartWithQuery('donation'),
  async (ctx) => {
    const amount = parseInt(ctx.callbackQuery.data.split(' ')[1], 10) * 100;
    
    await ctx.api.sendInvoice(ctx.chat.id, {
      ...donationProduct,
      prices: [{ label: 'Donation', amount }]
    });
    
    await new Promise(r => setTimeout(r, 500));
    await ctx.deleteMessage();
  }
);

// Pre-checkout
paymentRouter.preCheckoutQuery(async (ctx) => {
  await ctx.answerPreCheckoutQuery(true);
});

// Successful payment
paymentRouter.on('message:successful_payment', async (ctx) => {
  const { successful_payment } = ctx.message;
  logger.info('Successful payment:', successful_payment);
  
  if (successful_payment.invoice_payload.startsWith('donation')) {
    const sum = successful_payment.total_amount / 100;
    await ctx.reply(ctx.t('payment.successful_payment', { 
      sum, 
      currency: successful_payment.currency 
    }));
  } else if (successful_payment.invoice_payload.startsWith('buy_balance')) {
    const parts = successful_payment.invoice_payload.split(' ');
    const tokens = parseInt(parts[1], 10);
    
    await tokenizeService.update_user_token(ctx.from.id, tokens, 'add');
    await ctx.reply(ctx.t('payment.balance_topped_up', { tokens }));
    
    const { tokens: newTokens } = await tokenizeService.get_tokens(ctx.from.id);
    await ctx.reply(ctx.t('payment.current_balance', { tokens: newTokens }));
  }
});
