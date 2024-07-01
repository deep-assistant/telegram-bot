from datetime import datetime, time

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
        midnight_today = datetime.combine(now.date(), time(0, 0))
        last_check_data = self.get_check_date(user_id)

        if last_check_data is not None:
            last_check = datetime.fromisoformat(last_check_data)
            if last_check < now and now > midnight_today:
                token_entity = await self.get_tokens(user_id, GPTModels.GPT_3_5)
                tokens = token_entity.get('tokens')

                if tokens >= 50000:
                    return

                if tokens < 0:
                    await self.update_user_token(user_id, GPTModels.GPT_3_5, -1 * tokens + 50000)
                    self.set_check_date(user_id, now.isoformat())
                    return

                await self.update_user_token(user_id, GPTModels.GPT_3_5, 50000 - tokens)
                self.set_check_date(user_id, now.isoformat())

            else:
                print("Пока ещё не новый день 😴")
        else:
            token_entity = await self.get_tokens(user_id, GPTModels.GPT_3_5)
            await self.update_user_token(user_id, GPTModels.GPT_3_5, 50000 - token_entity.get('tokens'))
            self.set_check_date(user_id, now.isoformat())

    async def get_tokens(self, user_id: str, model: GPTModels):
        user_token = await self.get_user_tokens(user_id, model)

        if user_token is not None:
            return user_token
        else:
            await self.create_new_token(user_id=user_id, model=model)
            return await self.get_user_tokens(user_id, model)

    async def create_new_token(self, user_id: str, model: GPTModels):
        payload = {
            "token": ADMIN_TOKEN,
            "userName": get_user_name(user_id, model)
        }

        response = await async_post(f"{PROXY_URL}/generate-user-token", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка при создании токена: {response.text}")
            return None

    async def get_user_tokens(self, user_id: str, model: GPTModels):
        params = {
            "token": ADMIN_TOKEN,
            "userName": get_user_name(user_id, model)
        }

        response = await async_get(f"{PROXY_URL}/user-tokens", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                return data

        return None

    async def update_user_token(self, user_id: str, model: GPTModels, tokens: int, operation='add'):
        payload = {
            "token": ADMIN_TOKEN,
            "userName": get_user_name(user_id, model),
            "newToken": tokens,
            "operation": operation
        }

        response = await async_post(f"{PROXY_URL}/update-user-token", json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def clear_dialog(self, user_id: str, model: GPTModels):
        payload = {
            "token": ADMIN_TOKEN,
            "dialogName": get_user_name(user_id, model),
        }

        response = await async_post(f"{PROXY_URL}/clear-dialog", json=payload, headers=headers)

        if response.status_code == 200:
            return {"response": response.json(), "status": response.status_code}
        elif response.status_code == 404:
            return {"response": response.json(), "status": response.status_code}
        else:
            return None


tokenizeService = TokenizeService()
