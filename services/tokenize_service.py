from bot.utils import get_user_name
from config import PROXY_URL, ADMIN_TOKEN
from services import GPTModels
from services.utils import async_get, async_post

max_tokens = 50000

headers = {'Content-Type': 'application/json'}


class TokenizeService:
    async def get_tokens(self, user_id: str, model: GPTModels):
        user_token = await self.get_user_tokens(user_id, model)

        if user_token is not None:
            return user_token
        else:
            await self.create_new_token(user_id=user_id, model=model)
            await self.update_user_token(user_id=user_id, model=model, tokens=8500)
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

    async def update_user_token(self, user_id: str, model: GPTModels, tokens: int):
        payload = {
            "token": ADMIN_TOKEN,
            "userName": get_user_name(user_id, model),
            "newToken": tokens
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
