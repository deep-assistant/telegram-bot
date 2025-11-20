from typing import Dict, List, Optional
from config import PROXY_URL, ADMIN_TOKEN
from services.utils import async_get, async_post
from bot.utils import get_user_name

class TransferService:
    """Сервис для работы с переводами энергии"""
    
    async def get_settings(self) -> Optional[Dict]:
        """Получить настройки переводов"""
        params = {"masterToken": ADMIN_TOKEN}
        response = await async_get(f"{PROXY_URL}/transfer/settings", params=params)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    async def check_user_exists(self, username: str) -> Dict:
        """
        Проверить существование пользователя по username
        
        Args:
            username: Username с @ (например: @TimaxLacs)
            
        Returns:
            {
                "exists": bool,
                "user_id": str,
                "username": str,
                "full_name": str,
                "is_premium": bool
            }
        """
        params = {
            "masterToken": ADMIN_TOKEN,
            "username": username
        }
        
        response = await async_get(f"{PROXY_URL}/transfer/check-user", params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "exists": data.get("exists", False),
                "user_id": data.get("user_id"),
                "username": data.get("username"),
                "full_name": data.get("full_name"),
                "is_premium": data.get("is_premium", False)
            }
        
        return {"exists": False}
    
    async def execute_transfer(
        self, 
        sender_id: str, 
        receiver_id: str, 
        amount: int,
        sender_username: Optional[str] = None,
        sender_full_name: Optional[str] = None,
        receiver_username: Optional[str] = None,
        receiver_full_name: Optional[str] = None
    ) -> Dict:
        """
        Выполнить перевод
        
        Args:
            sender_id: User ID отправителя (Telegram ID)
            receiver_id: User ID получателя
            amount: Сумма перевода
            sender_username: Username отправителя (без @)
            sender_full_name: Полное имя отправителя
            receiver_username: Username получателя (без @)
            receiver_full_name: Полное имя получателя
            
        Returns:
            {
                "success": bool,
                "data": {...} или "error": str
            }
        """
        params = {"masterToken": ADMIN_TOKEN}
        
        payload = {
            "senderUserId": get_user_name(sender_id),
            "receiverUserId": receiver_id,
            "amount": amount
        }
        
        # Добавляем данные отправителя для синхронизации
        if sender_username or sender_full_name:
            payload["senderData"] = {}
            if sender_username:
                payload["senderData"]["username"] = sender_username
            if sender_full_name:
                payload["senderData"]["full_name"] = sender_full_name
        
        # Добавляем данные получателя для синхронизации
        if receiver_username or receiver_full_name:
            payload["receiverData"] = {}
            if receiver_username:
                payload["receiverData"]["username"] = receiver_username
            if receiver_full_name:
                payload["receiverData"]["full_name"] = receiver_full_name
        
        response = await async_post(
            f"{PROXY_URL}/transfer/execute",
            params=params,
            json=payload
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            error_data = response.json()
            return {
                "success": False,
                "error": error_data.get("message", "Неизвестная ошибка")
            }
    
    async def get_history(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict]:
        """
        Получить историю переводов
        
        Args:
            user_id: User ID
            limit: Максимальное количество записей
            
        Returns:
            List of transfers
        """
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": get_user_name(user_id),
            "limit": min(limit, 50)  # Макс 50
        }
        
        response = await async_get(f"{PROXY_URL}/transfer/history", params=params)
        
        if response.status_code == 200:
            return response.json().get("transfers", [])
        
        return []
    
    async def get_stats(self, user_id: str) -> Optional[Dict]:
        """
        Получить статистику переводов пользователя
        
        Args:
            user_id: User ID
            
        Returns:
            {
                "user_stats": {...},
                "today": {...},
                "recent_transfers": int
            }
        """
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": get_user_name(user_id)
        }
        
        response = await async_get(f"{PROXY_URL}/transfer/stats", params=params)
        
        if response.status_code == 200:
            return response.json()
        
        return None

transferService = TransferService()

