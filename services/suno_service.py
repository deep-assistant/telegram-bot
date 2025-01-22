import asyncio

from config import GO_API_KEY
from services.utils import async_post, async_get


class SunoService:
    async def generate_suno(self, prompt, task_id_get):
        # 1. Create the task using the new /api/v1/task endpoint
        response = await async_post(
            "https://api.goapi.ai/api/v1/task",
            headers={
                'X-API-Key': GO_API_KEY,
                'Content-Type': 'application/json'
            },
            json={
                "model": "music-s",              # formerly "Suno" is now "music-s"
                "task_type": "generate_music",   # descriptive text prompt mode
                "input": {
                    "gpt_description_prompt": prompt,
                    "make_instrumental": False    # set to True if you need an instrumental only
                },
                "config": {
                    "service_mode": "public",
                    "webhook_config": {
                        "endpoint": "",           # optional
                        "secret": ""             # optional
                    }
                }
            }
        )

        # 2. Extract the task_id from the response
        task_id = response.json()['data']['task_id']
        if task_id:
            await task_id_get(task_id)  # If you need to store or log the task_id

        # 3. Poll the task status until it is not processing anymore, or give up after 15 attempts
        attempts = 0
        while True:
            if attempts == 15:
                return {}  # Return an empty result if it’s stuck in processing after 15 tries

            await asyncio.sleep(30)
            attempts += 1

            result = await self.task_fetch(task_id)
            # If the status is still "processing", keep waiting
            if result["data"].get("status") == "processing":
                continue

            # Otherwise, return the final result JSON
            return result

    async def task_fetch(self, task_id):
        # 4. Updated polling endpoint
        url = f"https://api.goapi.ai/api/v1/task/{task_id}"
        response = await async_get(
            url,
            headers={
                'X-API-Key': GO_API_KEY,
                'Content-Type': 'application/json'
            }
        )
        return response.json()


sunoService = SunoService()