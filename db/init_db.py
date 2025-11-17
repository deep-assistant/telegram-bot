import os

import vedis

# Путь к базе данных (можно переопределить через переменную окружения)
DB_PATH = os.getenv('DB_PATH', '/app/data/data_base.db')
data_base = vedis.Vedis(DB_PATH)


def db_key(user_id, key):
    return f"{user_id}_{key}"
