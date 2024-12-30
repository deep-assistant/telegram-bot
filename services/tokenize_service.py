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


tokenizeService = TokenizeService()
