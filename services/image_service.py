import logging
from random import randint
from requests import get

def txt2img(prompt, negative_prompt, model, scheduler, guidance_scale, steps, seed=randint(1, 10000)):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    }
    resp = get(
        "https://api.prodia.com/generate",
        params={
            "new": "true",
            "prompt": prompt,
            "model": model,
            "negative_prompt": "(nsfw:1.5),verybadimagenegative_v1.3, ng_deepnegative_v1_75t, (ugly face:0.5),cross-eyed,sketches, (worst quality:2), (low quality:2.1), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, bad anatomy, DeepNegative, facing away, tilted head, {Multiple people}, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worstquality, low quality, normal quality, jpegartifacts, signature, watermark, username, blurry, bad feet, cropped, poorly drawn hands, poorly drawn face, mutation, deformed, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, extra fingers, fewer digits, extra limbs, extra arms,extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed,mutated hands, polar lowres, bad body, bad proportions, gross proportions, text, error, missing fingers, missing arms, missing legs, extra digit, extra arms, extra leg, extra foot, repeating hair" + negative_prompt,
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
        resp = get(f"https://api.prodia.com/job/{data['job']}", headers=headers)
        json = resp.json()
        if json["status"] == "succeeded":
            return {"output": [f"https://images.prodia.xyz/{data['job']}.png"], "meta": {"seed": seed}}


class ImageService:
    default_model = "ICantBelieveItsNotPhotography_seco.safetensors [4e7a3dfd]"

    def generate(self, prompt: str):

        return txt2img(
            prompt=prompt,
            model=self.default_model,
            negative_prompt="",
            scheduler="DPM++ SDE Karras",
            guidance_scale=7,
            steps=25,
        )


imageService = ImageService()