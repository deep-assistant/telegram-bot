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

# Webhook performance and security settings
WEBHOOK_MAX_CONNECTIONS = 40  # Max simultaneous connections from Telegram
WEBHOOK_SECRET_TOKEN = ""  # Optional secret token for webhook validation
WEBHOOK_MAX_REQUESTS_PER_MINUTE = 100  # Rate limiting per user
WEBHOOK_METRICS_ENABLED = False  # Enable metrics endpoint at /metrics

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# HTTPX Configuration
# Controls SSL certificate verification for all HTTP requests made through services/utils.py
# Set to True to disable SSL verification (useful for development with self-signed certificates)
HTTPX_DISABLE_SSL_VERIFY = False

