from bot.utils import get_user_name
from config import PROXY_URL, ADMIN_TOKEN
from db import data_base, db_key
from services.utils import async_get, async_post, async_delete, async_put

max_tokens = 50000

headers = {'Content-Type': 'application/json'}


class TokenizeService:
    LAST_CHECK_DATE = "last_check_date"

    def get_check_date(self, user_id: str):
        try:
            return data_base[db_key(user_id, self.LAST_CHECK_DATE)].decode('utf-8')
        except KeyError:
            return None

    def set_check_date(self, user_id, value):
        with data_base.transaction():
            data_base[db_key(user_id, self.LAST_CHECK_DATE)] = value
        data_base.commit()

    async def get_tokens(self, user_id: str):
        user_token = await self.get_user_tokens(user_id)
        if user_token is not None:
            return user_token
        else:
            await self.create_new_token(user_id)
            return await self.get_user_tokens(user_id)

    async def create_new_token(self, user_id: str):
        payload = {
            "masterToken": ADMIN_TOKEN,
            "userId": get_user_name(user_id),
        }

        response = await async_post(f"{PROXY_URL}/token", params=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def get_user_tokens(self, user_id: str):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": get_user_name(user_id),
        }

        response = await async_get(f"{PROXY_URL}/token", params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                return {**data, "tokens": response.json()["tokens_gpt"]}

        return None

    async def update_token(self, user_id: str, tokens: int, operation='add'):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": get_user_name(user_id),
        }

        json = {
            "operation": operation,
            "amount": tokens
        }

        response = await async_put(f"{PROXY_URL}/token", params=params, json=json, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def clear_dialog(self, user_id: str):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": get_user_name(user_id),
        }

        response = await async_delete(f"{PROXY_URL}/dialogs", params=params, headers=headers)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            return None

    async def history(self, user_id: str):
        payload = {
            "masterToken": ADMIN_TOKEN,
            "dialogName": get_user_name(user_id),
        }
        response = await async_get(f"{PROXY_URL}/dialog-history", params=payload, headers=headers)
        if response.status_code == 200:
            return {"response": response.json(), "status": response.status_code}
        elif response.status_code == 404:
            return {"status": response.status_code}
        else:
            return None

    async def get_token(self, user_id: str):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
        }

        response = await async_get(f"{PROXY_URL}/token", params=params, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def regenerate_api_token(self, user_id: str):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
        }

        response = await async_post(f"{PROXY_URL}/token", params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    # ========== AdLean Integration: Request Counter ==========
    
    REQUESTS_COUNT_KEY = "requests_count"

    def get_requests_count(self, user_id: str) -> int:
        """
        Получить количество запросов пользователя
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            int: Количество запросов (0 если пользователь новый)
        """
        try:
            count = data_base[db_key(user_id, self.REQUESTS_COUNT_KEY)].decode('utf-8')
            return int(count)
        except KeyError:
            # Пользователь новый, счетчик = 0
            return 0
        except Exception as e:
            print(f"[TokenizeService] Error getting requests count: {e}")
            return 0

    def increment_requests_count(self, user_id: str) -> int:
        """
        Увеличить счетчик запросов на 1
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            int: Новое значение счетчика
        """
        current_count = self.get_requests_count(user_id)
        new_count = current_count + 1
        
        with data_base.transaction():
            data_base[db_key(user_id, self.REQUESTS_COUNT_KEY)] = str(new_count)
        data_base.commit()
        
        print(f"[TokenizeService] User {user_id} requests count: {new_count}")
        return new_count

    def reset_requests_count(self, user_id: str):
        """
        Сбросить счетчик запросов (опционально)
        
        Args:
            user_id: ID пользователя Telegram
        """
        with data_base.transaction():
            data_base[db_key(user_id, self.REQUESTS_COUNT_KEY)] = "0"
        data_base.commit()
        print(f"[TokenizeService] User {user_id} requests count reset")


tokenizeService = TokenizeService()
