from typing import Any

from openai import OpenAI

from bot.utils import get_user_name
from config import PROXY_URL, ADMIN_TOKEN, KEY_DEEPINFRA
from services.gpt_service import GPTModels
from services.utils import async_post

history = {}


class CompletionsService:
    TOKEN_LIMIT = 4096

    openai = OpenAI(
        api_key=KEY_DEEPINFRA,
        base_url="https://api.deepinfra.com/v1/openai",
    )

    def clear_history(self, user_id: str, ):
        history[user_id] = []

    def get_history(self, user_id: str, ):
        if not (user_id in history):
            history[user_id] = []

        return history[user_id]

    def update_history(self, user_id: str, history_item):
        self.get_history(user_id).append(history_item)

    def cut_history(self, user_id: str):
        dialog = self.get_history(user_id)

        reverted_dialog = list(reversed(dialog))

        cut_dialog = []

        symbols = 0

        for item in reverted_dialog:
            if symbols >= 6000:
                continue

            cut_dialog.append(item)

        history[user_id] = list(reversed(cut_dialog))

    async def query_open_source_model(self, user_id: str, message: str):
        self.update_history(user_id, {"role": "user", "content": message})
        self.cut_history(user_id)

        chat_completion = self.openai.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            max_tokens=4096,
            messages=self.get_history(user_id),
            stream=False,
        )

        content = chat_completion.choices[0].message.content

        self.update_history(user_id, {"role": "assistant", "content": content})

        return {"success": True, "response": chat_completion.choices[0].message.content}

    async def query_chatgpt(self, user_id, message, system_message, gpt_model: str, bot_model: GPTModels) -> Any:

        if bot_model.value is not GPTModels.GPT_4o.value and bot_model.value is not GPTModels.GPT_3_5.value:
            return await self.query_open_source_model(user_id, message)

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

        response = await async_post(f"{PROXY_URL}/chatgpt", json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "response": f"Ошибка 😔: {response.json().get('message')}"}


completionsService = CompletionsService()
