# 🧪 Тестовое Окружение Telegram Bot

## ⚡ Быстрый Старт

```bash
# 1. Скопируйте .env файл
cp .env.example .env.test

# 2. Отредактируйте .env.test (укажите TELEGRAM_TOKEN)
nano .env.test

# 3. Запустите контейнер
docker-compose -f docker-compose.test.yml up -d --build

# 4. Проверьте логи
docker logs -f telegram_bot_test
```

**✅ Готово!** Бот подключен к тестовому API на `http://localhost:8089`

---

## 📋 Содержание

- [Требования](#требования)
- [Детальная настройка](#детальная-настройка)
- [Конфигурация](#конфигурация)
- [Запуск и управление](#запуск-и-управление)
- [Тестирование](#тестирование)
- [Отличия от PROD](#отличия-от-prod)
- [Troubleshooting](#troubleshooting)
- [Workflow разработки](#workflow-разработки)

---

## 🔧 Требования

### Обязательно

- Docker & Docker Compose установлены
- Тестовый резейл API запущен на `localhost:8089`
- Telegram Bot Token (от @BotFather)

### Проверка готовности API

```bash
# Проверьте что тестовый API работает
curl http://localhost:8089/v1/chat/completions \
  -H "Authorization: Bearer test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'
```

Если видите ответ от API - можно продолжать!

---

## 📝 Детальная Настройка

### Шаг 1: Подготовка окружения

```bash
cd /home/resale/resale-ai/deepgpt-test/telegram-bot
```

### Шаг 2: Создание .env.test файла

```bash
cp .env.example .env.test
```

### Шаг 3: Заполнение конфигурации

Откройте `.env.test` и настройте:

```env
# ==========================================
# КРИТИЧЕСКИ ВАЖНЫЕ ПАРАМЕТРЫ
# ==========================================

# Ваш токен от @BotFather
TELEGRAM_TOKEN=your_test_bot_token

# API тестового резейла (НЕ МЕНЯЙТЕ!)
PROXY_URL=http://localhost:8089

# Тестовый токен API (НЕ МЕНЯЙТЕ!)
ADMIN_TOKEN=test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# ==========================================
# ОПЦИОНАЛЬНЫЕ ПАРАМЕТРЫ
# ==========================================

# Можно оставить как есть или заполнить
KEY_DEEPINFRA=your_key
GO_API_KEY=your_key
GUO_GUO_KEY=your_key
OPENROUTER_API_KEY=your_key
PAYMENTS_TOKEN=your_token
ADLEAN_API_KEY=your_key
```

### Шаг 4: Проверка конфигурации

```bash
# Просмотрите содержимое файла
cat .env.test | grep -v "^#" | grep -v "^$"

# Убедитесь что:
# ✅ PROXY_URL=http://localhost:8089
# ✅ ADMIN_TOKEN=test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
# ✅ TELEGRAM_TOKEN заполнен
```

---

## ⚙️ Конфигурация

### Ключевые параметры для TEST

| Параметр | Значение TEST | Значение PROD | Описание |
|----------|---------------|---------------|----------|
| `PROXY_URL` | `http://localhost:8089` | `https://api.deep.assistant.run.place` | URL тестового API |
| `ADMIN_TOKEN` | `test_a1b2c3d4...` | `677bafc4f788...` | Токен доступа к API |
| `TELEGRAM_TOKEN` | Тестовый бот | Продакшн бот | Токен Telegram |
| `IS_DEV` | `True` | `False` | Режим разработки |

### Остальные параметры

Все остальные параметры (KEY_DEEPINFRA, GO_API_KEY и т.д.) можно использовать те же, что и в PROD - они не критичны для тестирования основного функционала.

---

## 🚀 Запуск и Управление

### Первый запуск

```bash
# Сборка и запуск
docker-compose -f docker-compose.test.yml up -d --build

# Проверка статуса
docker ps | grep telegram_bot_test

# Просмотр логов в реальном времени
docker logs -f telegram_bot_test
```

### Перезапуск после изменений

```bash
# Остановить
docker-compose -f docker-compose.test.yml down

# Пересобрать и запустить
docker-compose -f docker-compose.test.yml up -d --build
```

### Быстрый перезапуск (без пересборки)

```bash
docker-compose -f docker-compose.test.yml restart
```

### Просмотр логов

```bash
# Последние 100 строк
docker logs --tail 100 telegram_bot_test

# В реальном времени
docker logs -f telegram_bot_test

# Сохранить в файл
docker logs telegram_bot_test > bot_logs.txt
```

### Остановка

```bash
# Остановить контейнер
docker-compose -f docker-compose.test.yml stop

# Остановить и удалить
docker-compose -f docker-compose.test.yml down

# Удалить вместе с образом
docker-compose -f docker-compose.test.yml down --rmi all
```

---

## 🧪 Тестирование

### Проверка подключения к API

```bash
# Войдите в контейнер
docker exec -it telegram_bot_test bash

# Проверьте переменные окружения
echo $PROXY_URL
echo $ADMIN_TOKEN

# Попробуйте запрос к API
curl http://localhost:8089/v1/chat/completions \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"test"}]}'
```

### Тестирование бота

1. **Найдите бота в Telegram** по токену от @BotFather
2. **Отправьте** `/start`
3. **Проверьте логи**:
   ```bash
   docker logs -f telegram_bot_test
   ```
4. **Отправьте сообщение** боту
5. **Убедитесь** что запросы идут через `localhost:8089`

### Мониторинг запросов

```bash
# В одном терминале - логи бота
docker logs -f telegram_bot_test

# В другом терминале - логи API
docker logs -f chatgpt_proxy_test

# Отправьте сообщение боту и наблюдайте
```

---

## 🔄 Отличия от PROD

| Аспект | TEST | PROD |
|--------|------|------|
| **API URL** | `http://localhost:8089` | `https://api.deep.assistant.run.place` |
| **Admin Token** | `test_a1b2c3d4...` | `677bafc4f788...` |
| **Сеть Docker** | `network_mode: host` | По умолчанию |
| **База данных** | `data_base_test.db` | `data_base.db` |
| **Контейнер** | `telegram_bot_test` | `telegram_bot_prod` |
| **SSL** | Нет (HTTP) | Да (HTTPS) |

---

## 🐛 Troubleshooting

### Бот не запускается

```bash
# Проверьте логи
docker logs telegram_bot_test

# Проверьте что контейнер работает
docker ps -a | grep telegram_bot_test

# Проверьте .env файл
cat .env.test
```

**Частые ошибки:**
- ❌ `TELEGRAM_TOKEN` не заполнен
- ❌ API не запущен на `localhost:8089`
- ❌ Неверный `ADMIN_TOKEN`

### API недоступен

```bash
# Проверьте что тестовый API работает
docker ps | grep chatgpt_proxy_test

# Проверьте порт
curl http://localhost:8089

# Если не отвечает - запустите API
cd /home/resale/resale-ai/deepgpt-test/api-gateway
docker-compose -f docker-compose.test.yml up -d
```

### Бот не отвечает на сообщения

1. **Проверьте логи бота**:
   ```bash
   docker logs -f telegram_bot_test
   ```

2. **Проверьте логи API**:
   ```bash
   docker logs -f chatgpt_proxy_test
   ```

3. **Проверьте баланс токенов**:
   ```bash
   # Посмотрите файл tokens.json
   cat /home/resale/resale-ai/deepgpt-test/api-gateway/src/db/tokens.json
   ```

### Ошибка "Connection refused"

**Причина:** Docker контейнер не может достать `localhost:8089`

**Решение:** Убедитесь что в `docker-compose.test.yml`:
```yaml
network_mode: "host"  # ← Эта строка обязательна!
```

---

## 💻 Workflow Разработки

### 1. Внесение изменений

```bash
# Редактируйте код
nano bot/gpt/router.py

# Пересоберите и перезапустите
docker-compose -f docker-compose.test.yml up -d --build

# Проверьте изменения
docker logs -f telegram_bot_test
```

### 2. Тестирование

```bash
# Отправьте сообщения боту в Telegram
# Наблюдайте за логами

# Проверьте что запросы идут через тестовый API
docker logs -f chatgpt_proxy_test | grep "POST /completions"
```

### 3. Заливка в Git

```bash
cd /home/resale/resale-ai/deepgpt-test/telegram-bot

# Проверьте изменения
git status

# Добавьте файлы (БЕЗ .env.test!)
git add bot/ services/ config.py

# Коммит
git commit -m "Feature: добавил новую функцию"

# Пуш в ветку test
git push origin test
```

### 4. Деплой в PROD (после тестирования)

```bash
# В PROD репозитории
cd /home/resale/resale-ai/prod/telegram-bot

# Подтяните изменения
git pull origin main

# Перезапустите PROD
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📊 Полезные Команды

### Информация о контейнере

```bash
# Статус
docker ps | grep telegram_bot_test

# Детальная информация
docker inspect telegram_bot_test

# Использование ресурсов
docker stats telegram_bot_test
```

### Работа с базой данных

```bash
# Скопировать базу из контейнера
docker cp telegram_bot_test:/data_base.db ./data_base_test_backup.db

# Посмотреть размер
ls -lh data_base_test.db

# Удалить базу (для чистого старта)
rm -f data_base_test.db
docker-compose -f docker-compose.test.yml restart
```

### Очистка

```bash
# Удалить остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune

# Полная очистка
docker system prune -a
```

---

## 📚 Дополнительные Ресурсы

- **API Gateway (TEST)**: [README-TEST.md](../api-gateway/README-TEST.md)
- **Основная документация**: [README.md](README.md)
- **PROD документация**: [README-PROD.md](README-PROD.md)

---

## 💡 Советы

1. **Всегда проверяйте API перед запуском бота**
2. **Используйте `docker logs -f` для отладки**
3. **Не коммитьте `.env.test` в Git**
4. **Регулярно делайте бэкапы `data_base_test.db`**
5. **Тестируйте ВСЕ изменения перед деплоем в PROD**

---

**Нужна помощь?** Проверьте [Troubleshooting](#troubleshooting) или посмотрите логи!

