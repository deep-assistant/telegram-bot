"""
Сервис синхронизации данных пользователей из Telegram в БД
"""
import asyncio
import sys
from typing import Dict, List
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from config import ADMIN_TOKEN, PROXY_URL
from services.utils import async_post, async_get
from bot.utils import get_user_name


class UserSyncService:
    """Сервис для синхронизации данных пользователей"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def get_all_users(self) -> List[Dict]:
        """
        Получить всех пользователей из БД через API
        
        Returns:
            Список пользователей с их данными
        """
        try:
            params = {"masterToken": ADMIN_TOKEN}
            print(f"   🌐 GET {PROXY_URL}/tokens")
            response = await async_get(
                f"{PROXY_URL}/tokens",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📦 Raw response data: {data}")
                tokens = data.get("tokens", [])
                print(f"   ✅ Получено {len(tokens)} пользователей")
                if tokens:
                    print(f"   🔎 Первый элемент (type={type(tokens[0])}): {tokens[0]}")
                return tokens
            else:
                print(f"   ❌ Ошибка API: статус {response.status_code}")
                print(f"   Response: {response.text}")
                return []
        except Exception as e:
            print(f"   ❌ Исключение при запросе к API: {e}")
            return []
    
    async def sync_user_data(self, user_id: str, username: str = None, full_name: str = None) -> bool:
        """
        Синхронизировать данные пользователя в БД через API
        
        Args:
            user_id: User ID пользователя
            username: Username (без @)
            full_name: Полное имя
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            params = {"masterToken": ADMIN_TOKEN}
            payload = {
                "userId": user_id,
                "userData": {}
            }
            
            if username:
                payload["userData"]["username"] = username
            if full_name:
                payload["userData"]["full_name"] = full_name
            
            # Если нет данных для обновления, пропускаем
            if not payload["userData"]:
                print(f"      ⚠️  Нет данных для обновления")
                return True
            
            print(f"      🌐 POST {PROXY_URL}/tokens/sync")
            print(f"      📦 Payload: {payload}")
            
            response = await async_post(
                f"{PROXY_URL}/tokens/sync",
                params=params,
                json=payload
            )
            
            if response.status_code == 200:
                print(f"      ✅ API ответил успешно (200)")
                return True
            else:
                print(f"      ❌ Ошибка API: статус {response.status_code}")
                print(f"      Response: {response.text}")
                return False
        except Exception as e:
            print(f"      ❌ Исключение при синхронизации: {e}")
            return False
    
    async def fetch_telegram_data(self, user_id: str) -> Dict:
        """
        Получить актуальные данные пользователя из Telegram
        
        Args:
            user_id: User ID пользователя
            
        Returns:
            {
                "username": str или None,
                "full_name": str или None,
                "success": bool
            }
        """
        try:
            chat = await self.bot.get_chat(user_id)
            
            username = chat.username
            first_name = chat.first_name or ""
            last_name = chat.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            
            return {
                "username": username,
                "full_name": full_name if full_name else None,
                "success": True
            }
        except TelegramAPIError as e:
            print(f"Telegram API error for user {user_id}: {e}")
            return {"username": None, "full_name": None, "success": False}
        except Exception as e:
            print(f"Error fetching Telegram data for user {user_id}: {e}")
            return {"username": None, "full_name": None, "success": False}
    
    async def sync_single_user(self, user: Dict) -> Dict:
        """
        Синхронизировать одного пользователя
        
        Args:
            user: Данные пользователя из БД
            
        Returns:
            {
                "user_id": str,
                "status": "synced" | "skipped" | "failed",
                "updated": bool,
                "reason": str (опционально)
            }
        """
        user_id = user.get("user_id")
        current_username = user.get("username")
        current_full_name = user.get("full_name")
        
        print(f"🔍 Проверка пользователя {user_id}:")
        print(f"   - Current username: {current_username}")
        print(f"   - Current full_name: {current_full_name}")
        
        # Проверить нужна ли синхронизация
        needs_sync = False
        reason_parts = []
        
        if not current_username or current_username == user_id:
            needs_sync = True
            reason_parts.append("no username")
            print(f"   ⚠️  Нужна синхронизация: нет username")
        
        if not current_full_name or current_full_name == "Unknown User":
            needs_sync = True
            reason_parts.append("no full_name")
            print(f"   ⚠️  Нужна синхронизация: нет full_name")
        
        # Проверка на неправильный формат (когда full_name содержит @)
        if current_full_name and current_full_name.startswith("@"):
            needs_sync = True
            reason_parts.append("full_name contains @")
            print(f"   ⚠️  Нужна синхронизация: full_name содержит @ ({current_full_name})")
        
        if not needs_sync:
            print(f"   ✅ Пропуск: данные валидны")
            return {
                "user_id": user_id,
                "status": "skipped",
                "updated": False,
                "reason": "data is valid"
            }
        
        # Получить актуальные данные из Telegram
        print(f"   📡 Запрос данных из Telegram API...")
        telegram_data = await self.fetch_telegram_data(user_id)
        
        if not telegram_data["success"]:
            print(f"   ❌ Не удалось получить данные из Telegram")
            return {
                "user_id": user_id,
                "status": "failed",
                "updated": False,
                "reason": "failed to fetch from Telegram"
            }
        
        print(f"   📥 Данные из Telegram:")
        print(f"      - Username: {telegram_data['username']}")
        print(f"      - Full name: {telegram_data['full_name']}")
        
        # Синхронизировать в БД
        print(f"   💾 Сохранение в БД...")
        sync_success = await self.sync_user_data(
            user_id,
            username=telegram_data["username"],
            full_name=telegram_data["full_name"]
        )
        
        if sync_success:
            print(f"   ✅ Успешно синхронизирован!")
            return {
                "user_id": user_id,
                "status": "synced",
                "updated": True,
                "reason": ", ".join(reason_parts)
            }
        else:
            print(f"   ❌ Ошибка при сохранении в БД")
            return {
                "user_id": user_id,
                "status": "failed",
                "updated": False,
                "reason": "failed to update in DB"
            }
    
    async def sync_all_users(self, max_concurrent: int = 5) -> Dict:
        """
        Синхронизировать всех пользователей из БД
        
        Args:
            max_concurrent: Максимальное количество одновременных запросов
            
        Returns:
            {
                "total": int,
                "synced": int,
                "skipped": int,
                "failed": int,
                "details": List[Dict]
            }
        """
        print("\n" + "="*60, flush=True)
        print("🔄 НАЧАЛО СИНХРОНИЗАЦИИ ПОЛЬЗОВАТЕЛЕЙ", flush=True)
        print("="*60 + "\n", flush=True)
        sys.stdout.flush()
        
        # Получить всех пользователей
        print("📡 Запрос всех пользователей из БД через API...")
        users = await self.get_all_users()
        
        if not users:
            print("⚠️  НЕ НАЙДЕНО ПОЛЬЗОВАТЕЛЕЙ В БД!")
            print("="*60 + "\n")
            return {
                "total": 0,
                "synced": 0,
                "skipped": 0,
                "failed": 0,
                "details": []
            }
        
        print(f"📊 Найдено пользователей в БД: {len(users)}")
        print(f"⚙️  Максимум одновременных запросов: {max_concurrent}\n")
        
        # Синхронизация с ограничением конкурентности
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def sync_with_semaphore(user):
            async with semaphore:
                return await self.sync_single_user(user)
        
        # Выполнить синхронизацию для всех пользователей
        tasks = [sync_with_semaphore(user) for user in users]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обработать результаты
        synced = 0
        skipped = 0
        failed = 0
        details = []
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
                print(f"\n❌ ИСКЛЮЧЕНИЕ при синхронизации: {result}\n")
                continue
            
            if result["status"] == "synced":
                synced += 1
            elif result["status"] == "skipped":
                skipped += 1
            elif result["status"] == "failed":
                failed += 1
            
            details.append(result)
        
        summary = {
            "total": len(users),
            "synced": synced,
            "skipped": skipped,
            "failed": failed,
            "details": details
        }
        
        print("\n" + "="*60)
        print("📈 РЕЗУЛЬТАТЫ СИНХРОНИЗАЦИИ:")
        print("="*60)
        print(f"   Всего пользователей: {summary['total']}")
        print(f"   ✅ Синхронизировано: {summary['synced']}")
        print(f"   ⏭️  Пропущено (данные валидны): {summary['skipped']}")
        print(f"   ❌ Ошибок: {summary['failed']}")
        print("="*60 + "\n")
        
        return summary


# Singleton instance
_user_sync_service = None

def get_user_sync_service(bot: Bot = None) -> UserSyncService:
    """
    Получить синглтон инстанс UserSyncService
    
    Args:
        bot: Bot instance (обязателен при первом вызове)
    """
    global _user_sync_service
    
    if _user_sync_service is None:
        if bot is None:
            raise ValueError("Bot instance required for first call")
        _user_sync_service = UserSyncService(bot)
    
    return _user_sync_service

