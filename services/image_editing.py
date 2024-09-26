from config import GO_API_KEY
from services.utils import async_post


class ImageEditing:
    async def remove_background(self, image):
        headers = {
            "X-API-KEY": GO_API_KEY,
            "Content-Type": "application/json"
        }

        data = {
            "task_type": "background_remove",
            "result_type": "url",
            "task_input": {"image": image}
        }

        response = await async_post("https://api.goapi.ai/api/image_toolkit/v2/create", headers=headers, json=data)

        result = response.json()

        return await self.fetch_image_editing(result["data"]["task_id"])

    async def fetch_image_editing(self, task_id):
        headers = {
            "X-API-KEY": GO_API_KEY,
            "Content-Type": "application/json"
        }

        data = {"task_id": task_id}

        response = await async_post("https://api.goapi.ai/api/image_toolkit/v2/fetch", headers=headers, json=data)

        return response.json()


imageEditing = ImageEditing()
