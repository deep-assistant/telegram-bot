import { config } from '../../config.js';

export const productTest = {
  title: 'Подписка на бота',
  description: 'Активация подписки на бота на 1 месяц',
  provider_token: config.paymentsToken,
  currency: 'rub',
  photo_url: 'https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg',
  photo_width: 416,
  photo_height: 234,
  photo_size: 416,
  is_flexible: false,
  prices: [{ label: 'Подписка на 1 месяц', amount: 500 * 100 }],
  start_parameter: 'one-month-subscription',
  payload: 'test-invoice-payload'
};

export const donationProduct = {
  title: 'Пожертвование на развитие проекта.',
  description: `
🖥 Аренда серверов.                                         
🛠️ Создание инфраструктуры для нейросетей.                 
🦾 Оплата нейросетевых сервисов.                           
`,
  provider_token: config.paymentsToken,
  currency: 'rub',
  photo_url: 'https://storage.yandexcloud.net/gptutor-bucket/DEEP_LOGO.jpg',
  photo_width: 416,
  photo_height: 234,
  photo_size: 416,
  is_flexible: false,
  start_parameter: 'donation',
  payload: 'donation'
};

export const buyBalanceProduct = {
  title: 'Пополнение баланса',
  provider_token: config.paymentsToken,
  currency: 'RUB',
  photo_url: 'https://storage.yandexcloud.net/gptutor-bucket/DEEP_LOGO.jpg',
  photo_width: 416,
  photo_height: 234,
  photo_size: 416,
  is_flexible: false,
  start_parameter: 'buy_balance'
};
