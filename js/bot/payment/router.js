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
import { tokenizeService } from '../../services/index.js';
import { GPTModels } from '../../services/gpt_service.js';
import { createLogger } from '../../utils/logger.js';

const log = createLogger('payment_router');

export const paymentRouter = new Composer();

// Debug GPTModels
log.debug(() => 'GPTModels imported:', () => GPTModels);
log.debug(() => 'GPTModels.GPT_4o:', () => GPTModels?.GPT_4o);

// Pricing functions (matching Python logic)
function getStarPrice(tokens, model) {
  const baseStarPrice = 1.9;
  const baseOneTokenPrice = model === GPTModels.GPT_4o ? 0.0008 : 0.00025;
  log.debug('Calculating star price for', { tokens, model, baseOneTokenPrice });
  return Math.floor(tokens * baseOneTokenPrice / baseStarPrice);
}

function getPriceRub(tokens, model) {
  const baseOneTokenPrice = model === GPTModels.GPT_4o ? 0.0008 : 0.00025;
  log.debug('Calculating rub price for', { tokens, model, baseOneTokenPrice });
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
  log.debug('Creating buy balance keyboard model');
  const keyboard = new InlineKeyboard()
    .text(ctx.t('payment.gpt_4o'), `buy-gpt ${GPTModels.GPT_4o}`)
    .text(ctx.t('payment.gpt_3_5'), `buy-gpt ${GPTModels.GPT_3_5}`)
    .row();
  return keyboard;
}

function createBuyBalanceKeyboardMethod(ctx, model) {
  log.debug('Creating buy balance keyboard method for model:', model);
  const starsCallback = `buy_method_stars ${model} stars`;
  const cardCallback = `buy_method_card ${model} card`;
  
  const keyboard = new InlineKeyboard()
    .text(ctx.t('payment.telegram_stars'), starsCallback)
    .text(ctx.t('payment.card_payment'), cardCallback);
  
  return keyboard;
}

// /donut and /donation commands
paymentRouter.command('donut', async (ctx) => {
  log.debug('Donation command triggered');
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
  log.debug('Donation command triggered');
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
  log.debug('Buy command triggered');
  log.debug('Showing payment method selection for buy command');
  await ctx.reply(ctx.t('payment.choose_payment_method'), {
    reply_markup: createBuyBalanceKeyboardMethod(ctx, GPTModels.GPT_4o)
  });
});

paymentRouter.hears([BALANCE_PAYMENT_COMMAND_TEXT, '💎 Top up', '💎 Пополнить'], async (ctx) => {
  log.debug('Buy button triggered');
  log.debug('Showing payment method selection for buy button');
  await ctx.reply(ctx.t('payment.choose_payment_method'), {
    reply_markup: createBuyBalanceKeyboardMethod(ctx, GPTModels.GPT_4o)
  });
});

// Back to payment method selection
/*
paymentRouter.callbackQuery(
  StartWithQuery('back_buy_method'),
  async (ctx) => {
    const model = ctx.callbackQuery.data.split(' ')[1];
    log.trace('Back to payment method selection triggered for model:', model);
    console.log('Back to payment method - Full callback data:', ctx.callbackQuery.data);
    try {
      await ctx.editMessageText(ctx.t('payment.choose_payment_method'));
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardMethod(ctx, model) });
    } catch (error) {
      log.error('Error in back_buy_method:', error);
    }
  }
);
*/

// Handle buy-gpt callback (model selection)
/*
paymentRouter.callbackQuery(
  StartWithQuery('buy-gpt'),
  async (ctx) => {
    const model = ctx.callbackQuery.data.split(' ')[1];
    log.trace('Buy GPT model selected:', model);
    console.log('Buy GPT - Full callback data:', ctx.callbackQuery.data);
    log.trace('Showing payment method selection for model:', model);
    await ctx.editMessageText(ctx.t('payment.choose_payment_method'));
    await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardMethod(ctx, model) });
  }
);
*/

// Simple test handler for buy_method_stars
/*
paymentRouter.callbackQuery(
  (ctx) => {
    const result = ctx.callbackQuery.data === 'buy_method_stars gpt-4o stars';
    console.log('TEST: Exact match for buy_method_stars gpt-4o stars:', result);
    console.log('TEST: Actual callback data:', ctx.callbackQuery.data);
    return result;
  },
  async (ctx) => {
    console.log('SUCCESS: buy_method_stars handler triggered!');
    const model = ctx.callbackQuery.data.split(' ')[1];
    await ctx.editMessageText(ctx.t('payment.how_much_energy'));
    
    const prices = [25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000];
    const starPriceButtons = getStarPriceKeyboard('buy_stars', prices, model);
    log.trace('Star price buttons created:', starPriceButtons);
    
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
    log.trace('Final Stars keyboard created:', keyboard);
    
    await ctx.editMessageReplyMarkup({ reply_markup: keyboard });
  }
);
*/

// Telegram Stars selection (matching Python logic)
paymentRouter.on('callback_query', async (ctx) => {
  if (ctx.callbackQuery.data.startsWith('buy_method_stars')) {
    try {
      const model = ctx.callbackQuery.data.split(' ')[1];
      log.debug('Telegram Stars payment method selected for model:', model);
      log.debug('Showing energy amount selection for Stars');
      await ctx.editMessageText(ctx.t('payment.how_much_energy'));
      
      const prices = [25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000];
      const keyboard = new InlineKeyboard();
      
      // Create price buttons directly
      prices.forEach((price, index) => {
        const formatPrice = price.toLocaleString();
        const starPrice = getStarPrice(price, model);
        const buttonText = `${formatPrice}⚡️ (${starPrice} ⭐️)`;
        const callbackData = `buy_stars ${formatPrice} ${starPrice} ${model}`;
        
        keyboard.text(buttonText, callbackData);
        if (index % 2 === 1 || index === prices.length - 1) {
          keyboard.row();
        }
      });
      
      // Add back button
      keyboard.text(ctx.t('payment.back_to_payment_method'), `back_buy_method ${model}`);
      log.debug('Final Stars keyboard created', keyboard);
      
      await ctx.editMessageReplyMarkup({ reply_markup: keyboard });
    } catch (error) {
      log.error('Error in buy_method_stars handler:', error);
    }
    return;
  }
  
  if (ctx.callbackQuery.data.startsWith('buy_method_card')) {
    try {
      const model = ctx.callbackQuery.data.split(' ')[1];
      log.debug('Card payment method selected for model:', model);
      log.debug('Showing energy amount selection for Card');
      await ctx.editMessageText(ctx.t('payment.how_much_energy'));
      
      const prices = [100000, 250000, 500000, 1000000, 2500000, 5000000];
      const keyboard = new InlineKeyboard();
      
      // Create price buttons directly
      prices.forEach((price, index) => {
        const formatPrice = price.toLocaleString();
        const rubPrice = getPriceRub(price, model);
        const buttonText = `${formatPrice}⚡️ (${rubPrice} RUB)`;
        const callbackData = `buy_card ${formatPrice} ${rubPrice} ${model}`;
        
        keyboard.text(buttonText, callbackData);
        if (index % 2 === 1 || index === prices.length - 1) {
          keyboard.row();
        }
      });
      
      // Add back button
      keyboard.text(ctx.t('payment.back_to_payment_method'), `back_buy_method ${model}`);
      log.debug('Final Card keyboard created', keyboard);
      
      await ctx.editMessageReplyMarkup({ reply_markup: keyboard });
    } catch (error) {
      log.error('Error in buy_method_card handler:', error);
    }
    return;
  }
  
  if (ctx.callbackQuery.data.startsWith('back_buy_method')) {
    try {
      const model = ctx.callbackQuery.data.split(' ')[1];
      log.debug('Back to payment method selection triggered for model:', model);
      await ctx.editMessageText(ctx.t('payment.choose_payment_method'));
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardMethod(ctx, model) });
    } catch (error) {
      log.error('Error in back_buy_method:', error);
    }
    return;
  }
  
  if (ctx.callbackQuery.data.startsWith('back_buy_model')) {
    try {
      log.debug('Back to model selection triggered');
      await ctx.editMessageText(ctx.t('payment.choose_model'));
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardMethod(ctx) });
    } catch (error) {
      log.error('Error in back_buy_model:', error);
    }
    return;
  }
  
  if (ctx.callbackQuery.data.startsWith('buy-gpt')) {
    try {
      const model = ctx.callbackQuery.data.split(' ')[1];
      log.debug('Buy GPT model selected:', model);
      log.debug('Showing payment method selection for model:', model);
      await ctx.editMessageText(ctx.t('payment.choose_payment_method'));
      await ctx.editMessageReplyMarkup({ reply_markup: createBuyBalanceKeyboardMethod(ctx, model) });
    } catch (error) {
      log.error('Error in buy-gpt handler:', error);
    }
    return;
  }
  
  // Handle other callbacks (donation, buy_stars, buy_card, etc.)
  log.debug('Unknown callback:', ctx.callbackQuery.data);
});

// Send invoice for Stars (matching Python logic)
/*
paymentRouter.callbackQuery(
  StartWithQuery('buy_stars'),
  async (ctx) => {
    const tokens = ctx.callbackQuery.data.split(' ')[1];
    const amount = parseInt(ctx.callbackQuery.data.split(' ')[2]);
    const model = ctx.callbackQuery.data.split(' ')[3];
    log.trace('Buy stars triggered - tokens:', tokens, 'amount:', amount, 'model:', model);
    
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
*/

// Send invoice for card (matching Python logic)
/*
paymentRouter.callbackQuery(
  StartWithQuery('buy_card'),
  async (ctx) => {
    const tokens = ctx.callbackQuery.data.split(' ')[1];
    const amount = parseInt(ctx.callbackQuery.data.split(' ')[2]) * 100;
    const model = ctx.callbackQuery.data.split(' ')[3];
    log.trace('Buy card triggered - tokens:', tokens, 'amount:', amount, 'model:', model);
    
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
*/

// Handle donation
/*
paymentRouter.callbackQuery(
  StartWithQuery('donation'),
  async (ctx) => {
    const amount = parseInt(ctx.callbackQuery.data.split(' ')[1], 10) * 100;
    log.trace('Donation triggered - amount:', amount);
    
    await ctx.api.sendInvoice(ctx.chat.id, {
      ...donationProduct,
      prices: [{ label: ctx.t('payment.donation.label'), amount }]
    });
    
    await new Promise(r => setTimeout(r, 500));
    await ctx.deleteMessage();
  }
);
*/

// Pre-checkout
/*
paymentRouter.preCheckoutQuery(async (ctx) => {
  log.info(ctx.preCheckoutQuery);
  await ctx.answerPreCheckoutQuery(true);
});
*/

// Successful payment
/*
paymentRouter.on('message:successful_payment', async (ctx) => {
  const { successful_payment } = ctx.message;
  log.info('SUCCESSFUL PAYMENT:');
  for (const [k, v] of Object.entries(successful_payment)) {
    log.info(() => `${k} = ${v}`);
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
*/

// Simple test command
paymentRouter.command('test', async (ctx) => {
  log.debug('TEST COMMAND: Received test command');
  await ctx.reply('Test command works!');
});

// Simple test - replace all complex handlers temporarily
/*
paymentRouter.on('callback_query', async (ctx) => {
  console.log('ON METHOD: Received callback:', ctx.callbackQuery.data);
  
  if (ctx.callbackQuery.data.startsWith('buy_method_stars')) {
    console.log('SUCCESS: buy_method_stars detected!');
    await ctx.editMessageText('Telegram Stars selected!');
    return;
  }
  
  if (ctx.callbackQuery.data.startsWith('buy_method_card')) {
    console.log('SUCCESS: buy_method_card detected!');
    await ctx.editMessageText('Card payment selected!');
    return;
  }
  
  if (ctx.callbackQuery.data.startsWith('back_buy_method')) {
    console.log('SUCCESS: back_buy_method detected!');
    await ctx.editMessageText('Back to payment method!');
    return;
  }
  
  console.log('UNKNOWN CALLBACK:', ctx.callbackQuery.data);
  return false;
});
*/
