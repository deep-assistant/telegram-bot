import os

from aiogram.client.session import aiohttp
from aiogram.types import Message, FSInputFile


def include(arr: [str], value: str) -> bool:
    return len(list(filter(lambda x: value.startswith(x), arr))) > 0


def get_user_name(user_id: str):
    return str(user_id)


def divide_into_chunks(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def send_photo_as_file(message: Message, photo_url: str, caption, reply_markup=None):
    print(photo_url)
    photo_path = 'photo.jpg'

    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as response:
            if response.status == 200:
                with open(photo_path, 'wb') as f:
                    f.write(await response.read())

    returned_message = await message.answer_document(FSInputFile(photo_path), caption=caption, reply_markup=reply_markup)

    os.remove(photo_path)

    return returned_message
