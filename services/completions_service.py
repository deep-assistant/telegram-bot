from typing import Any

import requests

from bot.utils import get_user_name
from config import PROXY_URL, ADMIN_TOKEN
from services.gpt_service import GPTModels


class CompletionsService:
    TOKEN_LIMIT = 4096

    def query_chatgpt(self, user_id, message, system_message, gpt_model: str, bot_model: GPTModels) -> Any:

        payload = {
            'token': ADMIN_TOKEN,
            'dialogName': get_user_name(user_id, bot_model),
            'query': message,
            'tokenLimit': self.TOKEN_LIMIT,
            "userNameToken": get_user_name(user_id, bot_model),
            'singleMessage': False,
            'systemMessageContent': system_message,
            'model': gpt_model
        }

        response = requests.post(f"{PROXY_URL}/chatgpt", json=payload, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "response": f"Ошибка 😔: {response.json().get('message')}"}


completionsService = CompletionsService()
