import os

# ==========================================
# Telegram Bot Configuration
# ==========================================
# This file uses environment variables for configuration
# Copy .env.example to .env.test or .env.prod and fill in your values

# Telegram Bot
TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# Analytics
ANALYTICS_URL = os.getenv("ANALYTICS_URL", "https://6651b4300001d.tgrasp.co")

# API Configuration
PROXY_URL = os.getenv("PROXY_URL", "https://api.deep.assistant.run.place")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

# API Keys
KEY_DEEPINFRA = os.getenv("KEY_DEEPINFRA", "")
GO_API_KEY = os.getenv("GO_API_KEY", "")
GUO_GUO_KEY = os.getenv("GUO_GUO_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Development Mode
IS_DEV = os.getenv("IS_DEV", "True") == "True"

# Payments
PAYMENTS_TOKEN = os.getenv("PAYMENTS_TOKEN", "")

# Webhook Configuration
WEBHOOK_ENABLED = os.getenv("WEBHOOK_ENABLED", "False") == "True"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your.domain.com/webhook")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "3000"))

# AdLean Integration Settings
ADLEAN_API_KEY = os.getenv("ADLEAN_API_KEY", "")
ADLEAN_API_URL = os.getenv("ADLEAN_API_URL", "https://api.adlean.pro/engine/send_message")
ADLEAN_ENABLED = os.getenv("ADLEAN_ENABLED", "True") == "True"
ADLEAN_SHOW_AFTER_N_REQUESTS = int(os.getenv("ADLEAN_SHOW_AFTER_N_REQUESTS", "2"))

# HTTPX Configuration
# Controls SSL certificate verification for all HTTP requests made through services/utils.py
# Set to True to disable SSL verification (useful for development with self-signed certificates)
HTTPX_DISABLE_SSL_VERIFY = os.getenv("HTTPX_DISABLE_SSL_VERIFY", "False") == "True"

