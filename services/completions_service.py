import requests
import tiktoken

from config import GPT_TOKEN
from services.tokenize_service import tokenizeService

PROXY_URL = "http://173.212.230.201:8080/chatgpt"

contextName = "exampleDialog"

encoding = tiktoken.encoding_for_model("gpt-4")

max_tokens = 4096


class CompletionsService:
    TOKEN = GPT_TOKEN

    def query_chatgpt(self, user_id, message) -> str:
        if not tokenizeService.is_available_context(max_tokens, message):
            return "Слишком длинное сообщение!"

        payload = {
            'token': self.TOKEN,
            'query': message,
            'dialogName': user_id
        }

        response = requests.post(PROXY_URL, json=payload, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()

            print(data.get('response'))
            return data.get('response')
        else:
            return f"Ошибка: {response.text}"


completionsService = CompletionsService()
