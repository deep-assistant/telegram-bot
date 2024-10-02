from config import PROXY_URL, ADMIN_TOKEN
from services.utils import async_get, async_post


class SystemMessage:
    async def get_system_message(self, user_id):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
        }

        response = await async_get(f"{PROXY_URL}/system-message", params=params)

        return response.json()

    async def edit_system_message(self, user_id, message):
        params = {"masterToken": ADMIN_TOKEN, }
        json = {"userId": user_id, "message": message}

        response = await async_post(f"{PROXY_URL}/system-message", params=params, json=json)

        return response.json()


systemMessage = SystemMessage()
