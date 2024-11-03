import asyncio

from openai import OpenAI

from config import GO_API_KEY
from db import data_base, db_key
from services.image_utils import format_image_from_request, get_image_model_by_label
from services.utils import async_post, async_get

generating_map = {}


async def txt2img(prompt, negative_prompt, model, width, height, guidance_scale, steps, wait_image):
    response = await async_post(
        "https://api.midjourneyapi.xyz/sd/txt2img",
        headers={'X-API-Key': GO_API_KEY, 'Content-Type': 'application/json'},
        json={
            "prompt": prompt,
            "model_id": model,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "guidance_scale": guidance_scale,
            "num_inference_steps": steps,
            "lora_model": None,
            "lora_strength": None
        }
    )

    result = response.json()

    id = result["id"]

    if result["status"] == "processing":
        await wait_image()

        attempt = 0

        while True:
            if attempt == 30:
                return None

            await asyncio.sleep(30)
            response = await async_post("https://api.midjourneyapi.xyz/sd/fetch", json={"id": id})

            result = response.json()

            attempt += 1

            if result["status"] == "processing":
                continue

            return result

    return response.json()


class ImageService:
    CURRENT_IMAGE_MODEL = 'current_image_model'
    CURRENT_SAMPLER = 'current_sampler'
    CURRENT_STEPS = 'current_steps'
    CURRENT_CFG = 'current_cfg'
    CURRENT_SIZE = 'current_size'
    DALLE_SIZE = 'dalee_size'
    MIDJOURNEY_SIZE = 'midjourney_size'
    FLUX_MODEL = 'flux_model'

    default_model = "cyberrealistic"
    default_sampler = "DPM++SDEKarras"
    default_steps = 31
    default_cfg = "7"
    default_size = "512x512"
    default_dalle_size = "1024x1024"
    default_midjourney_size = "1:1"
    default_flux_model = "Qubico/flux1-dev"

    def set_waiting_image(self, user_id, value: bool):
        generating_map[user_id] = value

    def get_waiting_image(self, user_id):
        if not (user_id in generating_map):
            self.set_waiting_image(user_id, False)
            return False

        return generating_map[user_id]

    def get_current_image(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.CURRENT_IMAGE_MODEL)].decode('utf-8')
        except KeyError:
            self.set_current_image(user_id, self.default_model)
            return self.default_model

    def set_current_image(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_IMAGE_MODEL)] = state
        data_base.commit()

    def get_sampler(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.CURRENT_SAMPLER)].decode('utf-8')
        except KeyError:
            self.set_sampler_state(user_id, self.default_sampler)
            return self.default_sampler

    def set_sampler_state(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_SAMPLER)] = state
        data_base.commit()

    def get_steps(self, user_id: str):
        try:
            return data_base[db_key(user_id, self.CURRENT_STEPS)].decode('utf-8')
        except KeyError:
            self.set_steps_state(user_id, self.default_steps)
            return self.default_steps

    def set_steps_state(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_STEPS)] = state
        data_base.commit()

    def get_cfg_model(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.CURRENT_CFG)].decode('utf-8')
        except KeyError:
            self.set_cfg_state(user_id, self.default_cfg)
            return self.default_cfg

    def set_cfg_state(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_CFG)] = state
        data_base.commit()

    def get_size_model(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.CURRENT_SIZE)].decode('utf-8')
        except KeyError:
            self.set_size_state(user_id, self.default_size)
            return self.default_size

    def set_size_state(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_SIZE)] = state
        data_base.commit()

    def get_dalle_size(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.DALLE_SIZE)].decode('utf-8')
        except KeyError:
            self.set_dalle_size(user_id, self.default_dalle_size)
            return self.default_dalle_size

    def set_dalle_size(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.DALLE_SIZE)] = state
        data_base.commit()

    def get_midjourney_size(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.MIDJOURNEY_SIZE)].decode('utf-8')
        except KeyError:
            self.set_midjourney_size(user_id, self.default_midjourney_size)
            return self.default_midjourney_size

    def set_midjourney_size(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.MIDJOURNEY_SIZE)] = state
        data_base.commit()

    def get_flux_model(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.FLUX_MODEL)].decode('utf-8')
        except KeyError:
            self.set_flux_model(user_id, self.default_flux_model)
            return self.default_flux_model

    def set_flux_model(self, user_id: str, state: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.FLUX_MODEL)] = state
        data_base.commit()

    async def generate(self, prompt: str, user_id: str, wait_image):

        model = get_image_model_by_label(self.get_current_image(user_id))

        if not model:
            self.set_current_image(user_id, self.default_model)

        print(prompt)
        return await txt2img(
            prompt=prompt,
            height=self.get_size_model(user_id).split("x")[0],
            width=self.get_size_model(user_id).split("x")[1],
            model=get_image_model_by_label(self.get_current_image(user_id))["value"],
            negative_prompt="",
            guidance_scale=int(self.get_cfg_model(user_id)),
            steps=int(self.get_steps(user_id)),
            wait_image=wait_image
        )

    async def generate_dalle(self, user_id, prompt: str):
        openai = OpenAI(
            api_key=GO_API_KEY,
            base_url="https://api.goapi.xyz/v1/",
        )

        chat_completion = openai.chat.completions.create(
            model="gpt-4-gizmo-g-pmuQfob8d",
            max_tokens=30000,
            messages=[
                {
                    "role": "user",
                    "content": f"You should generate images in size {self.get_dalle_size(user_id)}"
                },
                {"role": "user", "content": prompt},
            ],
            stream=False,
        )

        formatted_response = format_image_from_request(chat_completion.choices[0].message.content)

        return {
            "image": formatted_response["image"],
            "text": formatted_response["text"],
            "total_tokens": chat_completion.usage.total_tokens
        }

    async def try_fetch_midjourney(self, task_id):
        await asyncio.sleep(10)

        attempts = 0

        while True:
            if attempts == 15:
                return {}

            await asyncio.sleep(30)
            attempts += 1

            result = await self.task_fetch(task_id)
            print(result)

            if result["status"] == "processing":
                continue

            return result

    async def generate_midjourney(self, user_id, prompt, task_id_get):
        data = {
            "prompt": prompt,
            "aspect_ratio": self.get_midjourney_size(user_id),
            "process_mode": "relax",
        }

        response = await async_post(
            "https://api.midjourneyapi.xyz/mj/v2/imagine",
            headers={"X-API-KEY": GO_API_KEY},
            json=data
        )

        task_id = response.json()['task_id']

        if task_id:
            await task_id_get(task_id)

        return await self.try_fetch_midjourney(task_id)

    async def task_fetch(self, task_id):
        response = await async_post("https://api.midjourneyapi.xyz/mj/v2/fetch", json={"task_id": task_id})
        return response.json()

    async def upscale_image(self, task_id, index, task_id_get):
        print(task_id)
        response = await async_post(
            "https://api.midjourneyapi.xyz/mj/v2/upscale",
            headers={"X-API-KEY": GO_API_KEY},
            json={"origin_task_id": task_id, "index": index, }
        )

        task_id = response.json()['task_id']

        if task_id:
            await task_id_get(task_id)

        return await self.try_fetch_midjourney(task_id)

    async def variation_image(self, task_id, index, task_id_get):
        response = await async_post(
            "https://api.midjourneyapi.xyz/mj/v2/variation",
            headers={"X-API-KEY": GO_API_KEY},
            json={"origin_task_id": task_id, "index": index, }
        )

        task_id = response.json()['task_id']

        if task_id:
            await task_id_get(task_id)

        return await self.try_fetch_midjourney(task_id)

    async def generate_flux(self, user_id, prompt, task_id_get):
        payload = {
            "model": self.get_flux_model(user_id),
            "task_type": "txt2img",
            "input": {"prompt": prompt}
        }

        headers = {
            'X-API-Key': GO_API_KEY,
            'Content-Type': 'application/json'
        }

        response = await async_post("https://api.goapi.ai/api/v1/task", headers=headers, json=payload)

        task_id = response.json()["data"]['task_id']

        attempts = 0

        await task_id_get(task_id)

        while True:
            if attempts == 10:
                return

            await asyncio.sleep(10)

            attempts += 1

            headers = {
                'X-API-Key': GO_API_KEY,
                'Content-Type': 'application/json'
            }

            response = await async_get(f"https://api.goapi.ai/api/v1/task/{task_id}", headers=headers)

            result = response.json()

            if result['data']['status'] == "pending":
                continue

            if result['data']['status'] == "processing":
                continue

            if result['data']['status'] == "completed":
                return result

    async def task_flux_fetch(self, task_id):
        headers = {
            'X-API-Key': GO_API_KEY,
            'Content-Type': 'application/json'
        }

        response = await async_get(f"https://api.goapi.ai/api/v1/task/{task_id}", headers=headers)
        return response.json()


imageService = ImageService()
