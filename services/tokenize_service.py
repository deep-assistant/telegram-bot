import requests

from bot.utils import get_user_name
from config import PROXY_URL, ADMIN_TOKEN
from services import GPTModels

max_tokens = 50000

headers = {'Content-Type': 'application/json'}


class TokenizeService:
    def get_tokens(self, user_id: str, model: GPTModels):
        user_token = self.get_user_tokens(user_id, model)

        if user_token is not None:
            return user_token
        else:
            self.create_new_token(user_id=user_id, model=model)
            return self.get_user_tokens(user_id, model)

    def create_new_token(self, user_id: str, model: GPTModels):
        payload = {
            "token": ADMIN_TOKEN,
            "userName": get_user_name(user_id, model)
        }

        response = requests.post(f"{PROXY_URL}/generate-user-token", json=payload, headers=headers)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print(f"Ошибка при создании токена: {response.text}")
            return None

    def get_user_tokens(self, user_id: str, model: GPTModels):
        params = {
            "token": ADMIN_TOKEN,
            "userName": get_user_name(user_id, model)
        }

        response = requests.get(f"{PROXY_URL}/user-tokens", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                return data

        return None

    def update_user_token(self, user_id: str, model: GPTModels, tokens: int):
        payload = {
            "token": ADMIN_TOKEN,
            "userName": get_user_name(user_id, model),
            "newToken": tokens
        }

        response = requests.post(f"{PROXY_URL}/update-user-token", json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def clear_dialog(self, user_id: str, model: GPTModels):
        payload = {
            "token": ADMIN_TOKEN,
            "dialogName": get_user_name(user_id, model),
        }

        response = requests.post(f"{PROXY_URL}/clear-dialog", json=payload, headers=headers)

        if response.status_code == 200:
            return {"response": response.json(), "status": response.status_code}
        elif response.status_code == 404:
            return {"response": response.json(), "status": response.status_code}
        else:
            return None


tokenizeService = TokenizeService()
