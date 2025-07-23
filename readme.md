# Bot startup ([русская версия](readme.ru.md))

0. Install dependencies:
```sh
pip3 install -r requirements.txt
```
1. Get a token from https://t.me/BotFather
2. Create config.py (be careful not to upload tokens to github)

```
cp config.example.py config.py
```

3. Specify require tokens and set specific settings:
```python
TOKEN = "" # Token from @BotFather
ANALYTICS_URL = "https://6651b4300001d.tgrasp.co"
PROXY_URL = "https://api.deep.assistant.run.place"
ADMIN_TOKEN = "" # Admin token for api.deep.assistant.run.place
KEY_DEEPINFRA = ""
IS_DEV = True
PAYMENTS_TOKEN = ""
GO_API_KEY = ""
GUO_GUO_KEY = ""
WEBHOOK_ENABLED = False  # or False to use polling
WEBHOOK_URL = "https://your.domain.com/webhook"
WEBHOOK_PATH = "/webhook"
WEBHOOK_HOST = "0.0.0.0"
WEBHOOK_PORT = 3000
```
4. Start the bot
```sh
python3 __main__.py
```