from typing import List
import os
import asyncio
import logging

import aiohttp
from aiogram.types import Message, FSInputFile

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


async def download_image(photo_url: str, file_path: str, skip_ssl: bool = SKIP_SSL_CHECK, max_retries: int = 3):
    """
    Download an image from a URL and save it to the given file path with retry logic.
    
    Args:
        photo_url (str): The URL of the image to download.
        file_path (str): The local file path where the image will be saved.
        skip_ssl (bool): If True, SSL certificate verification is skipped.
        max_retries (int): Maximum number of retry attempts.
    """
    # Configure connection with proper timeouts and limits
    timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_read=30)
    connector = aiohttp.TCPConnector(
        ssl=(not skip_ssl),
        limit=100,  # Total connection pool size limit
        limit_per_host=30,  # Per-host connection limit
        ttl_dns_cache=300,  # DNS cache TTL
        use_dns_cache=True,
        keepalive_timeout=30,
        enable_cleanup_closed=True
    )
    
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession(
                connector=connector, 
                timeout=timeout,
                raise_for_status=True
            ) as session:
                async with session.get(photo_url) as response:
                    if response.status == 200:
                        # Read the response in chunks to handle large files better
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return  # Success, exit the function
                    else:
                        response.raise_for_status()
                        
        except (aiohttp.ClientError, asyncio.TimeoutError, ConnectionResetError, OSError) as e:
            if attempt == max_retries:
                logging.error(f"Failed to download image after {max_retries + 1} attempts: {e}")
                raise  # Re-raise the last exception after all retries
            
            # Wait before retrying with exponential backoff
            wait_time = 2 ** attempt
            logging.warning(f"Download attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        
        except Exception as e:
            logging.error(f"Unexpected error during image download: {e}")
            raise  # Re-raise unexpected exceptions immediately

async def send_photo(message: Message, photo_url: str, caption, ext=".jpg", reply_markup=None):
    print(photo_url)
    photo_path = 'photo' + ext

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
    photo_path = 'photo' + ext

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
