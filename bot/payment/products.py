from aiogram import types

import config

TOKEN = config.PAYMENTS_TOKEN

product_test = {
    "title": "Подписка на бота",
    "description": "Активация подписки на бота на 1 месяц",
    "provider_token": TOKEN,
    "currency": "rub",
    "photo_url": "https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
    "photo_width": 416,
    "photo_height": 234,
    "photo_size": 416,
    "is_flexible": False,
    "prices": [types.LabeledPrice(label="Подписка на 1 месяц", amount=500 * 100)],
    "start_parameter": "one-month-subscription",
    "payload": "test-invoice-payload"
}

description = """
🖥 Аренда серверов.                                         \n     
🛠️ Создание инфраструктуры для нейросетей.                 \n     
🦾 Оплата нейросетевых сервисов.                           \n
                                                           \n
"""

donation_product = {
    "title": "Пожертвование на развитие проекта.",
    "description": description,
    "provider_token": TOKEN,
    "currency": "rub",
    "photo_url": "https://storage.yandexcloud.net/gptutor-bucket/DEEP_LOGO.jpg",
    "photo_width": 416,
    "photo_height": 234,
    "photo_size": 416,
    "is_flexible": False,
    "start_parameter": "donation",
    "payload": "donation"
}

buy_balance_product = {
    "title": "Пополнение баланса",
    "provider_token": TOKEN,
    "currency": "RUB",
    "photo_url": "https://storage.yandexcloud.net/gptutor-bucket/DEEP_LOGO.jpg",
    "photo_width": 416,
    "photo_height": 234,
    "photo_size": 416,
    "is_flexible": False,
    "start_parameter": "buy_balance",
}
