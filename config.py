import os
import sys

def get_required_env(key: str) -> str:
    """Get required environment variable or exit with error"""
    value = os.getenv(key)
    if not value:
        print(f"ERROR: Required environment variable {key} is not set!")
        print(f"Please set {key} in your .env file or environment")
        sys.exit(1)
    return value

def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    return os.getenv(key, str(default)).lower() in ('true', '1', 'yes')

def get_env_int(key: str, default: int) -> int:
    """Get integer environment variable"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


# ==========================================
# REQUIRED CONFIGURATION (NO DEFAULTS)
# ==========================================

# Telegram Bot Configuration
TOKEN = get_required_env("TELEGRAM_TOKEN")

# API Configuration
PROXY_URL = get_required_env("PROXY_URL")
ADMIN_TOKEN = get_required_env("ADMIN_TOKEN")

# API Keys
KEY_DEEPINFRA = get_required_env("KEY_DEEPINFRA")
GO_API_KEY = get_required_env("GO_API_KEY")
GUO_GUO_KEY = get_required_env("GUO_GUO_KEY")
OPENROUTER_API_KEY = get_required_env("OPENROUTER_API_KEY")

# Analytics
ANALYTICS_URL = get_required_env("ANALYTICS_URL")

# Payments
PAYMENTS_TOKEN = get_required_env("PAYMENTS_TOKEN")

# AdLean Integration
ADLEAN_API_KEY = get_required_env("ADLEAN_API_KEY")


# ==========================================
# OPTIONAL CONFIGURATION (WITH SAFE DEFAULTS)
# ==========================================

# Development Mode
IS_DEV = get_env_bool("IS_DEV", False)

# Webhook Configuration
WEBHOOK_ENABLED = get_env_bool("WEBHOOK_ENABLED", False)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your.domain.com/webhook")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = get_env_int("WEBHOOK_PORT", 3000)

# AdLean Settings
ADLEAN_API_URL = os.getenv("ADLEAN_API_URL", "https://api.adlean.pro/engine/send_message")
ADLEAN_ENABLED = get_env_bool("ADLEAN_ENABLED", True)
ADLEAN_SHOW_AFTER_N_REQUESTS = get_env_int("ADLEAN_SHOW_AFTER_N_REQUESTS", 2)

# HTTPX Configuration
HTTPX_DISABLE_SSL_VERIFY = get_env_bool("HTTPX_DISABLE_SSL_VERIFY", False)

# Database Path
DB_PATH = os.getenv("DB_PATH", "/app/data/data_base.db")

# User Synchronization
SYNC_ON_STARTUP = get_env_bool("SYNC_ON_STARTUP", True)
PASS_SYNC_BD = os.getenv("PASS_SYNC_BD", "10874356918")


# ==========================================
# CONFIGURATION VALIDATION
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONFIGURATION VALIDATION")
    print("=" * 60)
    print(f"✓ Telegram Token: {TOKEN[:10]}...{TOKEN[-5:]}")
    print(f"✓ Proxy URL: {PROXY_URL}")
    print(f"✓ Admin Token: {ADMIN_TOKEN[:10]}...{ADMIN_TOKEN[-5:]}")
    print(f"✓ Analytics URL: {ANALYTICS_URL}")
    print(f"✓ Development Mode: {IS_DEV}")
    print(f"✓ Webhook Enabled: {WEBHOOK_ENABLED}")
    print(f"✓ AdLean Enabled: {ADLEAN_ENABLED}")
    print(f"✓ Database Path: {DB_PATH}")
    print("=" * 60)
    print("✅ All required configuration loaded successfully!")
    print("=" * 60)

