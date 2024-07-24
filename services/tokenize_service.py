from datetime import datetime, time, timedelta

from bot.utils import get_user_name
from config import PROXY_URL, ADMIN_TOKEN
from db import data_base, db_key
from services import GPTModels, StateTypes
from services.utils import async_get, async_post

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

    async def check_tokens_update_tokens(self, user_id):
        now = datetime.now()
        last_check_data = self.get_check_date(user_id)
        TOKENS = 10000

        if last_check_data is not None:
            last_check = datetime.fromisoformat(last_check_data)
            midnight_today = datetime.combine(last_check.date() + timedelta(days=1), time(0, 0))

            if last_check < now and now > midnight_today:
                token_entity = await self.get_tokens(user_id)
                tokens = token_entity.get('tokens')

                if tokens >= TOKENS:
                    return

                if tokens < 0:
                    await self.update_user_token(user_id, -1 * tokens + TOKENS)
                    self.set_check_date(user_id, now.isoformat())
                    return

                print(50000 - tokens)
                await self.update_user_token(user_id, TOKENS - tokens)
                self.set_check_date(user_id, now.isoformat())

            else:
                print("Пока ещё не новый день 😴")
        else:
            token_entity = await self.get_tokens(user_id)
            await self.update_user_token(user_id, TOKENS - token_entity.get('tokens'))
            self.set_check_date(user_id, now.isoformat())

    async def get_tokens(self, user_id: str):
        user_token = await self.get_user_tokens(user_id)
        if user_token is not None:
            return user_token
        else:
            await self.create_new_token(user_id)
            return await self.get_user_tokens(user_id)

    async def create_new_token(self, user_id: str):
        payload = {
            "admin_token": ADMIN_TOKEN,
            "userName": get_user_name(user_id),
            "tokenNum": 1500,
            "type": "user"
        }

        response = await async_post(f"{PROXY_URL}/generate-token", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def get_user_tokens(self, user_id: str):
        params = {
            "admin_token": ADMIN_TOKEN,
            "tokenName": get_user_name(user_id),
            "type": "user"
        }

        response = await async_get(f"{PROXY_URL}/tokens", params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                return data

        return None

    async def update_user_token(self, user_id: str, tokens: int, operation='add'):
        payload = {
            "tokenAdmin": ADMIN_TOKEN,
            "userToken": get_user_name(user_id),
            "type": "user",
            "addTokenNum": tokens,
            "operation": operation
        }

        response = await async_post(f"{PROXY_URL}/update-token", json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def clear_dialog(self, user_id: str):
        payload = {
            "token": ADMIN_TOKEN,
            "dialogName": get_user_name(user_id),
        }

        response = await async_post(f"{PROXY_URL}/clear-dialog", json=payload, headers=headers)

        if response.status_code == 200:
            return {"response": response.json(), "status": response.status_code}
        elif response.status_code == 404:
            return {"response": response.json(), "status": response.status_code}
        else:
            return None

    async def get_api_token(self, user_id: str):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
        }

        response = await async_get(f"{PROXY_URL}/token/admin", params=params, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def regenerate_api_token(self, user_id: str):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
        }

        response = await async_post(f"{PROXY_URL}/token/admin", params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None


tokenizeService = TokenizeService()
