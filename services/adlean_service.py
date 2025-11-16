"""
Сервис для работы с AdLean API
Интеграция рекламы в ответы телеграм-бота
"""
import time
from typing import Optional, Dict, Any
from services.utils import async_post


class AdLeanService:
    """Сервис для получения рекламных объявлений от AdLean"""
    
    def __init__(self, api_key: str, api_url: str, enabled: bool = True):
        """
        Инициализация сервиса AdLean
        
        Args:
            api_key: API ключ для аутентификации
            api_url: URL эндпоинта AdLean API
            enabled: Флаг включения/выключения рекламы
        """
        self.api_key = api_key
        self.api_url = api_url
        self.enabled = enabled
        print(f"[AdLean] Service initialized (enabled={enabled})")
    
    async def get_ad(
        self, 
        user_id: str, 
        message_text: str, 
        user_metadata: Optional[Dict[str, Any]] = None,
        role: str = "assistant"
    ) -> Dict[str, Any]:
        """
        Получить рекламное объявление от AdLean
        
        Args:
            user_id: ID пользователя Telegram
            message_text: Текст ответа GPT (не запрос пользователя!)
            user_metadata: Дополнительные метаданные пользователя:
                - country: str - страна пользователя (например, "RU")
                - gender: str - пол пользователя ("male", "female", "unknown")
                - ip: str - IP адрес пользователя
            role: Роль отправителя ("assistant" для ответа GPT, "user" для запроса)
            
        Returns:
            Dict с ключами:
                - have_ads: bool - есть ли реклама для показа
                - content: str или dict - текст рекламы (если have_ads=True)
        
        Example:
            >>> response = await adlean_service.get_ad(
            ...     user_id="123456789",
            ...     message_text="Вот инструкция как выложить песню...",  # Ответ GPT!
            ...     user_metadata={"country": "RU", "gender": "unknown"}
            ... )
            >>> if response.get("have_ads"):
            ...     print(response.get("content"))
        """
        print(f"[AdLean Service] get_ad() called for user {user_id}")
        
        # Если реклама отключена, сразу возвращаем пустой результат
        if not self.enabled:
            print(f"[AdLean Service] Service DISABLED, returning no ads")
            return {"have_ads": False, "content": ""}
        
        print(f"[AdLean Service] Service ENABLED, proceeding with API request")
        
        try:
            # Ограничиваем длину текста для оптимизации
            text_to_send = message_text[:500] if isinstance(message_text, str) else "Запрос с медиа"
            print(f"[AdLean Service] Message text length: {len(message_text)} -> {len(text_to_send)} (truncated)")
            
            # Формируем payload согласно документации AdLean API
            payload = {
                "text": text_to_send,
                "role": role,  # "assistant" для ответа GPT, "user" для запроса
                "timestamp": int(time.time()),
                "chat_id": f"chat_{user_id}",
                "user_type": "non_authorized",
                "user_metadata": user_metadata or {
                    "country": "RU",
                    "gender": "unknown",
                    "ip": "0.0.0.0"
                }
            }
            
            print(f"[AdLean Service] Payload prepared: chat_id={payload['chat_id']}, timestamp={payload['timestamp']}")
            
            # Заголовки для аутентификации
            headers = {
                "accept": "application/json",
                "Auth": self.api_key,
                "Content-Type": "application/json"
            }
            
            print(f"[AdLean Service] Sending POST request to {self.api_url}...")
            
            # Отправляем запрос к AdLean API
            response = await async_post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=5.0  # 5 секунд таймаут - не блокируем бота надолго
            )
            
            print(f"[AdLean Service] Response received: status_code={response.status_code}")
            
            # Проверяем успешность запроса
            if response.status_code == 200:
                data = response.json()
                have_ads = data.get("have_ads", False)
                raw_content = data.get("content")
                
                # Обрабатываем content - может быть dict или str
                if isinstance(raw_content, dict):
                    # Новый формат API: {"insert_index": 0, "content": "текст"}
                    content = raw_content.get("content", "")
                    insert_index = raw_content.get("insert_index", 0)
                    print(f"[AdLean Service] Content format: dict (insert_index={insert_index})")
                else:
                    # Старый формат или просто строка
                    content = raw_content or ""
                    insert_index = 0
                    print(f"[AdLean Service] Content format: string")
                
                # Логируем для отладки
                content_length = len(content) if content else 0
                print(f"[AdLean Service] ✅ SUCCESS - User {user_id}: have_ads={have_ads}, content_length={content_length}")
                print(f"[AdLean Service] Full API response: {data}")
                
                if have_ads and content:
                    print(f"[AdLean Service] Ad content preview: {content[:100]}...")
                
                return {
                    "have_ads": have_ads,
                    "content": content,
                    "insert_index": insert_index
                }
            else:
                # В случае ошибки API, не показываем рекламу
                error_text = response.text[:200] if hasattr(response, 'text') else 'N/A'
                print(f"[AdLean Service] ❌ API ERROR: status_code={response.status_code}")
                print(f"[AdLean Service] Error response: {error_text}")
                return {"have_ads": False, "content": ""}
                
        except Exception as e:
            # Обрабатываем любые ошибки gracefully
            print(f"[AdLean Service] ❌ EXCEPTION: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[AdLean Service] Traceback: {traceback.format_exc()}")
            return {"have_ads": False, "content": ""}
    
    def set_enabled(self, enabled: bool):
        """
        Включить/выключить показ рекламы
        
        Args:
            enabled: True - включить, False - выключить
        """
        self.enabled = enabled
        print(f"[AdLean] Advertising {'enabled' if enabled else 'disabled'}")


# Singleton instance (будет инициализирован в bot_run.py)
adlean_service: Optional[AdLeanService] = None


def init_adlean_service(api_key: str, api_url: str, enabled: bool = True):
    """
    Инициализация глобального экземпляра AdLean сервиса
    
    Args:
        api_key: API ключ AdLean
        api_url: URL эндпоинта
        enabled: Включена ли реклама
    """
    global adlean_service
    adlean_service = AdLeanService(api_key, api_url, enabled)
    print(f"[AdLean] Global service initialized")
    return adlean_service


def get_adlean_service() -> Optional[AdLeanService]:
    """
    Получить текущий экземпляр AdLean сервиса
    
    Returns:
        AdLeanService instance или None если не инициализирован
    """
    return adlean_service

