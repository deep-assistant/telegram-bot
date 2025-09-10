from typing import List
import os

from aiogram.client.session import aiohttp
from aiogram.types import Message, FSInputFile
from services.utils import extract_human_readable_filename

# Global constant to control SSL certificate verification.
SKIP_SSL_CHECK = False

# Old version intruduces a bug (the system message 'deep' also triggers to model 'deepseek-chat')
# def include(arr: [str], value: str) -> bool:
#     return len(list(filter(lambda x: value.startswith(x), arr))) > 0

def include(arr: List[str], value: str) -> bool:
    trimmed_value = value.strip()
    return any(x.strip() == trimmed_value for x in arr)

def get_user_name(user_id: str):
    return str(user_id)


def divide_into_chunks(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def download_image(photo_url: str, file_path: str, skip_ssl: bool = SKIP_SSL_CHECK):
    """
    Download an image from a URL and save it to the given file path.
    
    Args:
        photo_url (str): The URL of the image to download.
        file_path (str): The local file path where the image will be saved.
        skip_ssl (bool): If True, SSL certificate verification is skipped.
    """
    # If skip_ssl is True, then we set ssl to False in the connector.
    connector = aiohttp.TCPConnector(ssl=(not skip_ssl))
    
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(photo_url) as response:
            if response.status == 200:
                with open(file_path, 'wb') as f:
                    f.write(await response.read())
            else:
                # Optionally, you could raise an exception or handle errors differently.
                response.raise_for_status()

async def send_photo(message: Message, photo_url: str, caption, ext=".jpg", reply_markup=None):
    print(photo_url)
    
    # Extract human-readable filename from URL
    filename = extract_human_readable_filename(photo_url)
    # Use extracted filename but keep the original extension logic if provided
    if ext != ".jpg":
        name_part, _ = os.path.splitext(filename)
        filename = name_part + ext
    
    photo_path = filename

    # Download the image
    await download_image(photo_url, photo_path)
    
    # Send the image as a photo message.
    returned_message = await message.answer_photo(
        FSInputFile(photo_path),
        caption=caption,
        reply_markup=reply_markup
    )

    os.remove(photo_path)
    return returned_message

async def send_photo_as_file(message: Message, photo_url: str, caption, ext=".jpg", reply_markup=None):
    print(photo_url)
    
    # Extract human-readable filename from URL
    filename = extract_human_readable_filename(photo_url)
    # Use extracted filename but keep the original extension logic if provided
    if ext != ".jpg":
        name_part, _ = os.path.splitext(filename)
        filename = name_part + ext
    
    photo_path = filename

    # Download the image
    await download_image(photo_url, photo_path)
    
    # Send the image as a document.
    returned_message = await message.answer_document(
        FSInputFile(photo_path),
        caption=caption,
        reply_markup=reply_markup
    )

    os.remove(photo_path)
    return returned_message
