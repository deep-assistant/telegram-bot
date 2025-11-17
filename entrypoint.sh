#!/bin/bash
set -e

echo "[Entrypoint] Starting Telegram Bot..."

# Создаем директорию для данных если её нет
mkdir -p /app/data

# Путь к базе данных
DB_PATH="/app/data/data_base.db"

# Проверяем и инициализируем базу данных
if [ ! -f "$DB_PATH" ]; then
    echo "[Entrypoint] Database file not found at $DB_PATH. Initializing..."
    
    # Создаем и инициализируем базу данных
    python3 -c "
import vedis
import sys

try:
    db = vedis.Vedis('$DB_PATH')
    db['_initialized'] = 'true'
    db.commit()
    db.close()
    print('[Entrypoint] Database initialized successfully at $DB_PATH')
except Exception as e:
    print(f'[Entrypoint] Error initializing database: {e}')
    sys.exit(1)
"
else
    echo "[Entrypoint] Database file exists: $(ls -lh $DB_PATH 2>/dev/null | awk '{print $5}' || echo 'unknown size')"
fi

# Проверяем переменные окружения
echo "[Entrypoint] Configuration:"
echo "  - PROXY_URL: ${PROXY_URL}"
echo "  - IS_DEV: ${IS_DEV}"
echo "  - Bot Token: ${TOKEN:0:10}...${TOKEN: -5}"
echo "  - DB Path: $DB_PATH"

# Запускаем основное приложение
echo "[Entrypoint] Starting application..."
exec python __main__.py

