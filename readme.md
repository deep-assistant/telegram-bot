# Запуск проекта

1. Получить токен в https://t.me/BotFather
2. Создать config.py 
```sh
    touch config.py
```
3. Указать следующее содержимое:
```python

TOKEN = "" #Указать токен из @BotFather
ANALYTICS_URL = "https://6651b4300001d.tgrasp.co"
PROXY_URL = "https://api.deep-foundation.tech"
ADMIN_TOKEN = "" # Токен админа в deep
KEY_DEEPINFRA = ""
IS_DEV = True
PAYMENTS_TOKEN = ""
GO_API_KEY = ""
GUO_GUO_KEY = ""
```
4. Запустить проект
```sh
python __main__.py
```