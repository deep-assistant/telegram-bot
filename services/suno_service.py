import asyncio

from config import GO_API_KEY
from services.utils import async_post, async_get


class SunoService:
    async def generate_suno(self, prompt):
        response = await async_post(
            "https://api.goapi.ai/api/suno/v1/music",
            headers={'X-API-Key': GO_API_KEY, 'Content-Type': 'application/json'},
            json={
                "custom_mode": False,
                "mv": "chirp-v3-5",
                "input": {
                    "gpt_description_prompt": prompt,  # your simple prompt
                    "make_instrumental": False
                }
            }
        )

        task_id = response.json()['data']['task_id']

        attempts = 0

        while True:
            if attempts == 15:
                return {}

            await asyncio.sleep(30)
            attempts += 1

            response = await self.task_fetch(task_id)

            result = response.json()

            if result["data"]["status"] == "processing":
                continue

            return result

    async def task_fetch(self, task_id):
        url = "https://api.goapi.ai/api/suno/v1/music/" + task_id

        return await async_get(url, headers={
            'X-API-Key': GO_API_KEY,
            'Content-Type': 'application/json'
        })


sunoService = SunoService()
