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

// Pricing functions (matching Python logic)
function getStarPrice(tokens, model) {
  const baseStarPrice = 1.9;
  const baseOneTokenPrice = model === GPTModels.GPT_4o ? 0.0008 : 0.00025;
  console.log(tokens * baseOneTokenPrice);
  return Math.floor(tokens * baseOneTokenPrice / baseStarPrice);
}

function getPriceRub(tokens, model) {
  const baseOneTokenPrice = model === GPTModels.GPT_4o ? 0.0008 : 0.00025;
  console.log(tokens * baseOneTokenPrice);
  return Math.floor(tokens * baseOneTokenPrice);
}

function strikethrough(number) {
  return String(number).split('').join('\u0336');
}

function getRubPriceKeyboard(baseCallback, prices, model) {
  const buttons = [];
  
  for (const price of prices) {
    const formatPrice = price.toLocaleString();
    const starPrice = getPriceRub(price, model);
    
    buttons.push([
      new InlineKeyboard().text(
        `${formatPrice}⚡️ (${starPrice} RUB)`,
        `${baseCallback} ${formatPrice} ${starPrice} ${model}`
      )
    ]);
  }
  
  return buttons;
}

function getStarPriceKeyboard(baseCallback, prices, model) {
  const buttons = [];
  
  for (const price of prices) {
    const formatPrice = price.toLocaleString();
    const starPrice = getStarPrice(price, model);
    
    buttons.push([
      new InlineKeyboard().text(
        `${formatPrice}⚡️ (${starPrice} ⭐️)`,
        `${baseCallback} ${formatPrice} ${starPrice} ${model}`
      )
    ]);
  }
  
  return buttons;
}

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

function createBuyBalanceKeyboardModel(ctx) {
  return new InlineKeyboard()
    .text(ctx.t('payment.gpt_4o'), `buy-gpt ${GPTModels.GPT_4o}`)
    .text(ctx.t('payment.gpt_3_5'), `buy-gpt ${GPTModels.GPT_3_5}`)
    .row();
}

function createBuyBalanceKeyboardMethod(ctx, model) {
  return new InlineKeyboard()
    .text(ctx.t('payment.telegram_stars'), `buy_method_stars ${model} stars`)
    .text(ctx.t('payment.card_payment'), `buy_method_card ${model} card`)
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

// /buy commands - should show payment method selection directly (like Python)
paymentRouter.command('buy', async (ctx) => {
  logger.debug('Buy command triggered');
  await ctx.reply(ctx.t('payment.choose_payment_method'), {
    reply_markup: createBuyBalanceKeyboardMethod(ctx, GPTModels.GPT_4o)
  });
});

paymentRouter.hears([BALANCE_PAYMENT_COMMAND_TEXT, '💎 Top up', '💎 Пополнить'], async (ctx) => {
  logger.debug('Buy button triggered');
  await ctx.reply(ctx.t('payment.choose_payment_method'), {
    reply_markup: createBuyBalanceKeyboardMethod(ctx, GPTModels.GPT_4o)
  });
});

// Back to model selection
paymentRouter.callbackQuery(
  StartWithQuery('back_buy_model'),
  async (ctx) => {
    try {
      await ctx.editMessageText(ctx.t('payment.choose_model'));
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardModel(ctx) });
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
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardMethod(ctx, model) });
    } catch (error) {
      logger.error('Error in back_buy_method:', error);
    }
  }
);

// Telegram Stars selection (matching Python logic)
paymentRouter.callbackQuery(
  StartWithQuery('buy_method_stars'),
  async (ctx) => {
    const model = ctx.callbackQuery.data.split(' ')[1];
    await ctx.editMessageText(ctx.t('payment.how_much_energy'));
    
    const prices = [25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000];
    const starPriceButtons = getStarPriceKeyboard('buy_stars', prices, model);
    
    const keyboard = new InlineKeyboard();
    
    // Add price buttons
    starPriceButtons.forEach((buttonRow, index) => {
      keyboard.text(buttonRow[0].text, buttonRow[0].callback_data);
      if (index % 2 === 1 || index === starPriceButtons.length - 1) {
        keyboard.row();
      }
    });
    
    // Add back button
    keyboard.text(ctx.t('payment.back_to_payment_method'), `back_buy_method ${model}`);
    
    await ctx.editMessageReplyMarkup({ reply_markup: keyboard });
  }
);

// Card payment selection (matching Python logic)
paymentRouter.callbackQuery(
  StartWithQuery('buy_method_card'),
  async (ctx) => {
    const model = ctx.callbackQuery.data.split(' ')[1];
    await ctx.editMessageText(ctx.t('payment.how_much_energy'));
    
    const prices = [100000, 250000, 500000, 1000000, 2500000, 5000000];
    const rubPriceButtons = getRubPriceKeyboard('buy_card', prices, model);
    
    const keyboard = new InlineKeyboard();
    
    // Add price buttons
    rubPriceButtons.forEach((buttonRow, index) => {
      keyboard.text(buttonRow[0].text, buttonRow[0].callback_data);
      if (index % 2 === 1 || index === rubPriceButtons.length - 1) {
        keyboard.row();
      }
    });
    
    // Add back button
    keyboard.text(ctx.t('payment.back_to_payment_method'), `back_buy_method ${model}`);
    
    await ctx.editMessageReplyMarkup({ reply_markup: keyboard });
  }
);

// Send invoice for Stars (matching Python logic)
paymentRouter.callbackQuery(
  StartWithQuery('buy_stars'),
  async (ctx) => {
    const tokens = ctx.callbackQuery.data.split(' ')[1];
    const amount = parseInt(ctx.callbackQuery.data.split(' ')[2]);
    const model = ctx.callbackQuery.data.split(' ')[3];
    
    await ctx.api.sendInvoice(ctx.chat.id, {
      title: ctx.t('payment.purchase_energy'),
      description: ctx.t('payment.buy_energy_question', { tokens }),
      payload: `buy_balance ${tokens.replace(',', '')} ${model} stars`,
      provider_token: config.paymentsToken,
      currency: 'XTR',
      prices: [{ label: 'XTR', amount }],
      reply_markup: new InlineKeyboard().text(ctx.t('payment.pay_stars', { amount }), true).row()
    });
    
    await new Promise(r => setTimeout(r, 500));
    await ctx.deleteMessage();
  }
);

// Send invoice for card (matching Python logic)
paymentRouter.callbackQuery(
  StartWithQuery('buy_card'),
  async (ctx) => {
    const tokens = ctx.callbackQuery.data.split(' ')[1];
    const amount = parseInt(ctx.callbackQuery.data.split(' ')[2]) * 100;
    const model = ctx.callbackQuery.data.split(' ')[3];
    
    await ctx.api.sendInvoice(ctx.chat.id, {
      ...buyBalanceProduct,
      description: ctx.t('payment.buy_energy_question', { tokens }),
      payload: `buy_balance ${tokens.replace(',', '')} ${model} card`,
      prices: [{ label: ctx.t('payment.buy_energy_question', { tokens }), amount }],
      provider_data: JSON.stringify({
        receipt: {
          items: [{
            description: ctx.t('payment.buy_energy_question', { tokens }),
            quantity: "1",
            amount: {
              value: String(Math.floor(amount / 100)) + ".00",
              currency: "RUB",
            },
            vat_code: 1,
            payment_mode: "full_payment",
            payment_subject: "commodity"
          }],
          email: "edtimyr@gmail.com"
        }
      })
    });
    
    console.log("PAYMENTS_TOKEN");
    console.log(config.paymentsToken);
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
      prices: [{ label: ctx.t('payment.donation.label'), amount }]
    });
    
    await new Promise(r => setTimeout(r, 500));
    await ctx.deleteMessage();
  }
);

// Pre-checkout
paymentRouter.preCheckoutQuery(async (ctx) => {
  logger.info(ctx.preCheckoutQuery);
  await ctx.answerPreCheckoutQuery(true);
});

// Successful payment
paymentRouter.on('message:successful_payment', async (ctx) => {
  const { successful_payment } = ctx.message;
  logger.info('SUCCESSFUL PAYMENT:');
  for (const [k, v] of Object.entries(successful_payment)) {
    logger.info(`${k} = ${v}`);
  }
  
  if (successful_payment.invoice_payload.startsWith('donation')) {
    const sum = Math.floor(successful_payment.total_amount / 100);
    await ctx.reply(ctx.t('payment.successful_payment', { 
      sum, 
      currency: successful_payment.currency 
    }));
  } else if (successful_payment.invoice_payload.startsWith('buy_balance')) {
    const parts = successful_payment.invoice_payload.split(' ');
    const tokens = parseInt(parts[1], 10);
    
    await tokenizeService.get_tokens(ctx.from.id);
    await tokenizeService.update_user_token(ctx.from.id, tokens, 'add');
    
    if (parts[3] === 'stars') {
      await ctx.reply(ctx.t('payment.successful_payment_stars', { 
        amount: successful_payment.total_amount,
        currency: successful_payment.currency,
        tokens 
      }));
    } else {
      await ctx.reply(ctx.t('payment.successful_payment_card', { 
        amount: Math.floor(successful_payment.total_amount / 100),
        currency: successful_payment.currency,
        tokens 
      }));
    }
    
    const { tokens: newTokens } = await tokenizeService.get_tokens(ctx.from.id);
    await ctx.reply(ctx.t('payment.current_balance', { tokens: newTokens }));
  }
});
