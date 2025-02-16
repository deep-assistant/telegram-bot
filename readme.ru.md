# Запуск бота ([english version](readme.md))

0. Установить зависимости:
```sh
pip3 install -r requirements.txt
```
1. Получить токен в https://t.me/BotFather
2. Создать config.py (будьте осторожны не залить его на GitHub)

```
cp config.example.py config.py
```

3. Укажите необходиммые токены и конкретные настройки:
```python
TOKEN = "" #Указать токен из @BotFather
ANALYTICS_URL = "https://6651b4300001d.tgrasp.co"
PROXY_URL = "https://api.deep-foundation.tech"
ADMIN_TOKEN = "" # Токен админа в api.deep-foundation.tech
KEY_DEEPINFRA = ""
IS_DEV = True
PAYMENTS_TOKEN = ""
GO_API_KEY = ""
GUO_GUO_KEY = ""
WEBHOOK_ENABLED = False  # или False, чтобы использовать polling
WEBHOOK_URL = "https://your.domain.com/webhook"
WEBHOOK_PATH = "/webhook"
WEBHOOK_HOST = "0.0.0.0"
WEBHOOK_PORT = 3000
```
4. Запустить проект
```sh
python3 __main__.py
```