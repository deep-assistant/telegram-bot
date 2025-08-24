import asyncio
import json
import re
from typing import Any

from openai import OpenAI

from bot.utils import get_user_name
from bot.constants import DEFAULT_ERROR_MESSAGE
from config import PROXY_URL, ADMIN_TOKEN, KEY_DEEPINFRA, GO_API_KEY
from services.gpt_service import GPTModels
from services.utils import async_post

history = {}

# Temporary disable any free conversations (for investigation)
conversations = {
    # "9ac59cfb-2e73-4b08-82d1-c2d94a240fc2": True,
    # "c8f6b5b9-46a4-4f11-8679-4c74699c7f3d": True,
    # "7945e1db-b3f1-4e86-b000-584cff2d4d81": True,
    # "3886244e-1b61-4713-8bf9-b5af56fedde6": True,
    # "1d491883-1fe2-49b9-a422-917186b4329f": True,
    # "e970eece-6236-4ef4-a071-5cb1367aad6b": True,
    # "f851d10d-8094-4e1c-9545-8f5dffcb1b5f": True,
    # "95f3832b-f125-429b-9d16-c1b918fe20cc": True,
    # "84a8eec5-ee00-4ff0-9b35-1340b27140fa": True,
    # "99ce43fd-8ee0-4bd6-8ed0-f6930035dc7f": True
}

async def set_toggle_conversation(key, flag):
    await asyncio.sleep(1)
    conversations[key] = flag

async def get_free_conversation():
    while True:
        print(conversations)
        for key, value in conversations.items():
            if value:
                await set_toggle_conversation(key, False)
                return key

class CompletionsService:
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

    async def query_chatgpt(self, user_id, message, system_message, gpt_model: str, bot_model: GPTModels, singleMessage: bool) -> Any:

        params = {
            "masterToken": ADMIN_TOKEN
        }

        payload = {
            'userId': get_user_name(user_id),
            'content': message,
            'systemMessage': system_message,
            'model': gpt_model
        }

        response = await async_post(f"{PROXY_URL}/completions", json=payload, params=params)

        if response.status_code == 200:
            completions = response.json()

            print(json.dumps(completions, indent=4))

            response_content = completions['choices'][0]['message']['content']

            response_model = completions['model']

            reasoning_content = None

            first_think_tag_positon = response_content.find("<think>")
            last_think_tag_positon = response_content.find("</think>")

            if first_think_tag_positon != -1 and last_think_tag_positon != -1:
                reasoning_content = response_content[first_think_tag_positon:last_think_tag_positon + len("</think>")]
                
            print(f"reasoning_content: {reasoning_content}")

            final_content = response_content.replace(reasoning_content, "").strip() if reasoning_content else response_content
            
            print(f"final_content: {final_content}")

            if reasoning_content:
                return { 'success': True, 'reasoning': reasoning_content, "response": final_content, 'model': response_model }
            else:
                return { 'success': True, 'response': final_content, 'model': response_model }
        else:
            return { "success": False, "response": f"Ошибка 😔: {response.json().get('message')}" }

    async def get_file(self, parts, conversation):
        url = f"https://api.goapi.xyz/api/chatgpt/v1/conversation/{conversation}/download"

        payload = json.dumps({
            "file_id": parts[0]["asset_pointer"].split("file-service://")[1]
        })
        headers = {
            'X-API-Key': GO_API_KEY,
            'Content-Type': 'application/json'
        }

        response = await async_post(url, headers=headers, data=payload)

        return response.json()

    async def get_multi_modal_conversation(self, prompt, attempt: int = 0):
        if attempt == 3:
            return {"text": DEFAULT_ERROR_MESSAGE, "url_image": None}

        conversation = await get_free_conversation()

        url = f"https://api.goapi.xyz/api/chatgpt/v1/conversation/{conversation}"

        payload = json.dumps({
            "model": "gpt-4o",
            "content": {"content_type": "multimodal_text", "parts": [prompt]},
            "stream": True
        })

        headers = {'X-API-Key': GO_API_KEY, 'Content-Type': 'application/json'}

        response = await async_post(url, headers=headers, data=payload)

        images = []
        text = []
        print(response.text)
        if response.status_code == 200:
            for line in response.text.split("\n"):
                if line:
                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        try:
                            data_obj = json.loads(data_str)
                            content = data_obj["message"]["content"]
                            content_type = content["content_type"]
                            content = data_obj["message"]["content"]

                            if content is None:
                                continue

                            if content["parts"] is None:
                                continue

                            print(content["parts"])

                            content_parts = content["parts"][0]

                            if content_type == "multimodal_text":
                                images.append(content_parts)
                                continue

                            if content_type == "text":
                                text.append(content_parts)

                        except Exception as e:
                            print("Не удалось декодировать JSON:", e)
                            continue

            cleaned_text = re.sub(r"【[^】]*】", "", text[-1]).strip()

            if len(images) == 0:
                await set_toggle_conversation(conversation, True)
                return {"text": cleaned_text, "url_image": None}

            image_result = await self.get_file(images, conversation)

            result = {"text": cleaned_text, "url_image": image_result["data"]["download_url"]}
            await set_toggle_conversation(conversation, True)
            return result
        else:
            if response.status_code == 400:
                return await self.get_multi_modal_conversation(prompt, attempt + 1)
            print(f"Не удалось выполнить запрос. Статус-код: {response.status_code}")

            await asyncio.sleep(10)
            await set_toggle_conversation(conversation, True)
            return {"text": DEFAULT_ERROR_MESSAGE, "url_image": None}


completionsService = CompletionsService()
