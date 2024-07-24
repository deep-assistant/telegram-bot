import asyncio

from openai import OpenAI

from config import GO_API_KEY
from db import data_base, db_key
from services.image_utils import get_image_model_by_label, get_samplers_by_label, format_image_from_request
from services.utils import async_get

generating_map = {}


async def txt2img(prompt, negative_prompt, model, scheduler, guidance_scale, steps, seed="-1"):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    }

    print({
        "new": "true",
        "prompt": prompt,
        "model": model,
        "negative_prompt": "(nsfw:1.5),verybadimagenegative_v1.3, ng_deepnegative_v1_75t, (ugly face:0.5),cross-eyed,sketches, (worst quality:2), (low quality:2.1), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, bad anatomy, DeepNegative, facing away, tilted head, {Multiple people}, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worstquality, low quality, normal quality, jpegartifacts, signature, watermark, username, blurry, bad feet, cropped, poorly drawn hands, poorly drawn face, mutation, deformed, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, extra fingers, fewer digits, extra limbs, extra arms,extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed,mutated hands, polar lowres, bad body, bad proportions, gross proportions, text, error, missing fingers, missing arms, missing legs, extra digit, extra arms, extra leg, extra foot, repeating hair" + negative_prompt,
        "steps": steps,
        "cfg": guidance_scale,
        "seed": seed,
        "sampler": scheduler,
        "aspect_ratio": "square",
    })
    resp = await async_get(
        "https://api.prodia.com/generate",
        params={
            "new": "true",
            "prompt": prompt,
            "model": model,
            "negative_prompt": "(ugly face:0.5), cross-eyed, (worst quality:2), (low quality:2.1), normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, bad anatomy, owres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worstquality, low quality, normal quality, jpegartifacts, signature, watermark, username, blurry, bad feet, cropped, poorly drawn hands, poorly drawn face, mutation, deformed, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, extra fingers, fewer digits, extra limbs, extra arms,extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed,mutated hands, polar lowres, bad body, bad proportions, gross proportions, text, error, missing fingers, missing arms, missing legs, extra digit, extra arms, extra leg, extra foot, repeating hair" + negative_prompt,
            "steps": steps,
            "cfg": guidance_scale,
            "seed": seed,
            "sampler": scheduler,
            "aspect_ratio": "square",
        },
        headers=headers,
        timeout=30,
    )
    data = resp.json()

    while True:
        await asyncio.sleep(18)
        resp = await async_get(f"https://api.prodia.com/job/{data['job']}", headers=headers)
        json = resp.json()
        if json["status"] == "succeeded":
            return {"output": [f"https://images.prodia.xyz/{data['job']}.png"], "meta": {"seed": seed}}


class ImageService:
    CURRENT_IMAGE_MODEL = 'current_image_model'
    CURRENT_SAMPLER = 'current_sampler'
    CURRENT_STEPS = 'current_steps'
    CURRENT_CFG = 'current_cfg'
    DALLE_SIZE = 'dalee_size'

    default_model = "ICantBelieveItsNotPhotographySeco"
    default_sampler = "DPM++SDEKarras"
    default_steps = "20"
    default_cfg = "7"
    default_dalle_size = "1024x1024"

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

    def get_steps(self, user_id: str) -> str:
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

    async def generate(self, prompt: str, user_id: str):
        return await txt2img(
            prompt=prompt,
            model=get_image_model_by_label(self.get_current_image(user_id))["value"],
            negative_prompt="",
            scheduler=get_samplers_by_label(self.get_sampler(user_id))["value"],
            guidance_scale=int(self.get_cfg_model(user_id)),
            steps=int(self.get_steps(user_id)),
        )

    async def generate_dalle(self, user_id, prompt: str):
        openai = OpenAI(
            api_key=GO_API_KEY,
            base_url="https://api.goapi.xyz/v1/",
        )

        chat_completion = openai.chat.completions.create(
            model="gpt-4o-plus",
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


imageService = ImageService()
