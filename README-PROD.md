# 🚀 Production Окружение Telegram Bot

## ⚡ Быстрый Старт

```bash
# 1. Скопируйте .env файл
cp .env.example .env.prod

# 2. Отредактируйте .env.prod (заполните ВСЕ ключи!)
nano .env.prod

# 3. Запустите контейнер
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Проверьте логи
docker logs -f telegram_bot_prod
```

**✅ Готово!** Бот подключен к production API на `https://api.deep.assistant.run.place`

---

## 📋 Содержание

- [Требования](#требования)
- [Детальная настройка](#детальная-настройка)
- [Конфигурация](#конфигурация)
- [Запуск и управление](#запуск-и-управление)
- [Мониторинг](#мониторинг)
- [Backup и восстановление](#backup-и-восстановление)
- [Безопасность](#безопасность)
- [Обновление](#обновление)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Требования

### Обязательно

- Docker & Docker Compose установлены
- Production резейл API доступен на `https://api.deep.assistant.run.place`
- Production Telegram Bot Token (от @BotFather)
- Все API ключи (OpenAI, DeepInfra, etc.)
- Payments токен (для приема платежей)
- SSL сертификаты настроены (если используете Webhook)

### Проверка готовности API

```bash
# Проверьте что production API работает
curl https://api.deep.assistant.run.place/v1/chat/completions \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'
```

---

## 📝 Детальная Настройка

### Шаг 1: Подготовка сервера

```bash
# Зайдите на production сервер
ssh your-server

# Перейдите в директорию проекта
cd /home/resale/resale-ai/prod/telegram-bot

# Убедитесь что последняя версия
git pull origin main
```

### Шаг 2: Создание .env.prod файла

```bash
cp .env.example .env.prod
```

### Шаг 3: Заполнение ВСЕХ параметров

⚠️ **ВАЖНО:** В production все параметры должны быть заполнены!

```env
# ==========================================
# КРИТИЧЕСКИ ВАЖНЫЕ ПАРАМЕТРЫ
# ==========================================

# Production токен от @BotFather
TELEGRAM_TOKEN=your_production_bot_token

# Production API (НЕ МЕНЯЙТЕ!)
PROXY_URL=https://api.deep.assistant.run.place

# Production Admin Token
ADMIN_TOKEN=677bafc4f788f69d1f23c1881d49iuyt

# ==========================================
# API КЛЮЧИ (ВСЕ ОБЯЗАТЕЛЬНЫ!)
# ==========================================

KEY_DEEPINFRA=your_real_key
GO_API_KEY=your_real_key
GUO_GUO_KEY=your_real_key
OPENROUTER_API_KEY=your_real_key

# ==========================================
# ПЛАТЕЖИ (ОБЯЗАТЕЛЬНО!)
# ==========================================

PAYMENTS_TOKEN=your_real_payments_token

# ==========================================
# РЕКЛАМНАЯ ИНТЕГРАЦИЯ
# ==========================================

ADLEAN_API_KEY=your_real_adlean_key
ADLEAN_API_URL=https://api.adlean.pro/engine/send_message
ADLEAN_ENABLED=True
ADLEAN_SHOW_AFTER_N_REQUESTS=2

# ==========================================
# PRODUCTION НАСТРОЙКИ
# ==========================================

IS_DEV=False  # ← ОБЯЗАТЕЛЬНО False в production!

# Webhook (опционально, polling по умолчанию)
WEBHOOK_ENABLED=False
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PATH=/webhook
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=3000

ANALYTICS_URL=https://6651b4300001d.tgrasp.co
HTTPX_DISABLE_SSL_VERIFY=False
```

### Шаг 4: Проверка конфигурации

```bash
# Проверьте что файл создан
ls -la .env.prod

# Проверьте содержимое (БЕЗ ВЫВОДА В ТЕРМИНАЛ!)
cat .env.prod | wc -l  # Должно быть ~30 строк

# Проверьте критические параметры
grep "PROXY_URL" .env.prod
grep "IS_DEV" .env.prod

# Убедитесь что:
# ✅ PROXY_URL=https://api.deep.assistant.run.place
# ✅ IS_DEV=False
# ✅ TELEGRAM_TOKEN заполнен
```

---

## ⚙️ Конфигурация

### Критические параметры для PROD

| Параметр | Значение | Почему важно |
|----------|----------|--------------|
| `PROXY_URL` | `https://api.deep.assistant.run.place` | Production API |
| `ADMIN_TOKEN` | `677bafc4f788...` | Доступ к API |
| `TELEGRAM_TOKEN` | Production токен | Основной бот |
| `IS_DEV` | `False` | Отключает debug режим |
| `PAYMENTS_TOKEN` | Реальный токен | Прием платежей |

### Webhook vs Polling

**Polling (по умолчанию):**
- ✅ Проще настроить
- ✅ Не требует SSL
- ✅ Надежнее
- ❌ Небольшая задержка

```env
WEBHOOK_ENABLED=False
```

**Webhook (для высокой нагрузки):**
- ✅ Мгновенные обновления
- ✅ Меньше нагрузка на Telegram API
- ❌ Требует SSL сертификат
- ❌ Требует публичный IP

```env
WEBHOOK_ENABLED=True
WEBHOOK_URL=https://your-domain.com/webhook
```

---

## 🚀 Запуск и Управление

### Первый запуск

```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Проверка статуса
docker ps | grep telegram_bot_prod

# Просмотр логов
docker logs -f telegram_bot_prod

# Убедитесь что бот запустился успешно
# Ищите строку: "Bot started successfully"
```

### Graceful перезапуск

```bash
# Остановить, обновить и запустить
docker-compose -f docker-compose.prod.yml stop
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build

# Проверьте логи
docker logs --tail 50 telegram_bot_prod
```

### Быстрый перезапуск (без обновления кода)

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Обновление без простоя

```bash
# Запустите новый контейнер рядом
docker-compose -f docker-compose.prod.yml up -d --build --no-deps telegram_bot_prod_new

# После проверки удалите старый
docker stop telegram_bot_prod
docker rm telegram_bot_prod
docker rename telegram_bot_prod_new telegram_bot_prod
```

---

## 📊 Мониторинг

### Логи в реальном времени

```bash
# Последние 100 строк
docker logs --tail 100 telegram_bot_prod

# Следить за обновлениями
docker logs -f telegram_bot_prod

# Логи с отметками времени
docker logs -f --timestamps telegram_bot_prod

# Поиск ошибок
docker logs telegram_bot_prod | grep -i "error"
```

### Статус и ресурсы

```bash
# Статус контейнера
docker ps | grep telegram_bot_prod

# Использование ресурсов
docker stats telegram_bot_prod

# Детальная информация
docker inspect telegram_bot_prod

# Сколько работает
docker ps --format "{{.Names}}: {{.Status}}" | grep telegram_bot_prod
```

### Мониторинг базы данных

```bash
# Размер базы
ls -lh data_base.db

# Последнее изменение
stat data_base.db

# Копия для анализа
docker cp telegram_bot_prod:/data_base.db ./data_base_snapshot.db
```

### Мониторинг API запросов

```bash
# Логи API
docker logs -f chatgpt_proxy_prod | grep "POST /completions"

# Количество запросов за последний час
docker logs --since 1h telegram_bot_prod | grep "query_chatgpt" | wc -l

# Средний response time
docker logs telegram_bot_prod | grep "response_time" | awk '{sum+=$NF; count++} END {print sum/count}'
```

---

## 💾 Backup и Восстановление

### Автоматический backup (рекомендуется)

Создайте cron job:

```bash
# Откройте crontab
crontab -e

# Добавьте ежедневный backup в 3:00
0 3 * * * docker cp telegram_bot_prod:/data_base.db /backups/telegram_bot_$(date +\%Y\%m\%d).db
```

### Ручной backup

```bash
# Создайте директорию для бэкапов
mkdir -p /backups/telegram-bot

# Backup базы данных
docker cp telegram_bot_prod:/data_base.db /backups/telegram-bot/data_base_$(date +%Y%m%d_%H%M%S).db

# Backup конфигурации
cp .env.prod /backups/telegram-bot/.env.prod_$(date +%Y%m%d)

# Создайте архив
tar -czf /backups/telegram-bot_full_$(date +%Y%m%d).tar.gz /backups/telegram-bot/
```

### Восстановление из backup

```bash
# Остановите контейнер
docker-compose -f docker-compose.prod.yml stop

# Восстановите базу
cp /backups/telegram-bot/data_base_20250117.db ./data_base.db

# Запустите контейнер
docker-compose -f docker-compose.prod.yml start

# Проверьте логи
docker logs -f telegram_bot_prod
```

### Disaster Recovery

```bash
# Полное восстановление с нуля
cd /home/resale/resale-ai/prod/telegram-bot

# 1. Получите код
git clone https://github.com/your-repo/telegram-bot
cd telegram-bot
git checkout main

# 2. Восстановите конфигурацию
cp /backups/.env.prod_20250117 .env.prod

# 3. Восстановите базу
cp /backups/data_base_20250117.db data_base.db

# 4. Запустите
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🔒 Безопасность

### Защита .env файлов

```bash
# Правильные права доступа
chmod 600 .env.prod

# Владелец - только ваш пользователь
chown $USER:$USER .env.prod

# Проверка
ls -la .env.prod
# Должно быть: -rw------- 1 user user
```

### Ротация токенов

```bash
# Регулярно обновляйте токены
# 1. Получите новый токен от @BotFather
# 2. Обновите .env.prod
nano .env.prod  # TELEGRAM_TOKEN=новый_токен

# 3. Перезапустите
docker-compose -f docker-compose.prod.yml restart
```

### Мониторинг безопасности

```bash
# Проверьте логи на подозрительную активность
docker logs telegram_bot_prod | grep -i "unauthorized\|failed\|denied"

# Проверьте открытые порты
docker port telegram_bot_prod

# Проверьте сетевые подключения
docker exec telegram_bot_prod netstat -tulpn
```

---

## 🔄 Обновление

### Стандартное обновление

```bash
# 1. Backup
docker cp telegram_bot_prod:/data_base.db /backups/before_update_$(date +%Y%m%d).db

# 2. Pull обновлений
git pull origin main

# 3. Проверьте changelog
git log --oneline -10

# 4. Обновите и перезапустите
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Проверьте логи
docker logs -f telegram_bot_prod

# 6. Тестируйте бота
# Отправьте /start и проверьте ответы
```

### Откат к предыдущей версии

```bash
# 1. Остановите контейнер
docker-compose -f docker-compose.prod.yml stop

# 2. Откатите код
git log --oneline -10  # Найдите нужный коммит
git checkout <commit_hash>

# 3. Восстановите базу
cp /backups/before_update_20250117.db data_base.db

# 4. Перезапустите
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🐛 Troubleshooting

### Бот не отвечает

```bash
# 1. Проверьте что контейнер работает
docker ps | grep telegram_bot_prod

# 2. Проверьте логи
docker logs --tail 100 telegram_bot_prod

# 3. Проверьте API
curl https://api.deep.assistant.run.place

# 4. Проверьте сеть
docker exec telegram_bot_prod ping -c 3 api.deep.assistant.run.place
```

### Ошибки API

```bash
# Проверьте логи API
docker logs chatgpt_proxy_prod | grep "ERROR"

# Проверьте баланс токенов
cat /home/resale/resale-ai/resale-chatgpt-azure/src/db/tokens.json

# Проверьте подключение
docker exec telegram_bot_prod curl -v https://api.deep.assistant.run.place
```

### Проблемы с платежами

```bash
# Проверьте PAYMENTS_TOKEN
grep PAYMENTS_TOKEN .env.prod

# Проверьте логи платежей
docker logs telegram_bot_prod | grep "payment"

# Тест платежного токена
# Отправьте тестовый платеж в боте
```

### Высокая нагрузка

```bash
# Проверьте использование ресурсов
docker stats telegram_bot_prod

# Проверьте количество пользователей
docker exec telegram_bot_prod sqlite3 data_base.db "SELECT COUNT(*) FROM users;"

# Увеличьте ресурсы в docker-compose.prod.yml
# resources:
#   limits:
#     memory: 2G
#     cpus: "2.0"
```

---

## 📈 Масштабирование

### Горизонтальное масштабирование

Если один инстанс не справляется:

```yaml
# docker-compose.prod.yml
services:
  telegram_bot_prod_1:
    # ... конфигурация
  
  telegram_bot_prod_2:
    # ... конфигурация
    
  nginx:
    # Load balancer
```

### Вертикальное масштабирование

```yaml
# docker-compose.prod.yml
services:
  telegram_bot_prod:
    # ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## 📚 Дополнительные Ресурсы

- **TEST документация**: [README-TEST.md](README-TEST.md)
- **API Gateway (PROD)**: `https://api.deep.assistant.run.place`
- **Основная документация**: [README.md](README.md)

---

## 💡 Best Practices

1. ✅ **Всегда делайте backup перед обновлением**
2. ✅ **Тестируйте изменения в TEST окружении**
3. ✅ **Мониторьте логи регулярно**
4. ✅ **Используйте `IS_DEV=False`**
5. ✅ **Храните `.env.prod` в безопасном месте**
6. ✅ **Ротируйте токены раз в квартал**
7. ✅ **Настройте автоматические бэкапы**
8. ✅ **Документируйте все изменения**

---

## 🚨 Emergency Contacts

В случае критических проблем:

1. **Проверьте статус** всех сервисов
2. **Посмотрите логи** за последний час
3. **Откатитесь** к последнему стабильному бэкапу
4. **Уведомите команду** о проблеме

```bash
# Быстрая диагностика
docker ps -a
docker logs --tail 200 telegram_bot_prod
docker logs --tail 200 chatgpt_proxy_prod
```

---

**Production - это серьезно!** Будьте осторожны с изменениями! 🚀

