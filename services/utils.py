import httpx
import config
import re
from urllib.parse import urlparse, unquote
import os


def get_httpx_client_kwargs():
    """Get common httpx client configuration from config."""
    kwargs = {}

    if getattr(config, 'HTTPX_DISABLE_SSL_VERIFY', False):
        kwargs['verify'] = False

    return kwargs


async def async_post(url, data=None, json=None, headers=None, timeout=None, files=None, params=None):
    client_kwargs = get_httpx_client_kwargs()

    async with httpx.AsyncClient(**client_kwargs) as client:
        response = await client.post(url, params=params, data=data, json=json, headers=headers, timeout=timeout,
                                     files=files)
        return response


async def async_put(url, data=None, json=None, headers=None, timeout=None, files=None, params=None):
    client_kwargs = get_httpx_client_kwargs()

    async with httpx.AsyncClient(**client_kwargs) as client:
        response = await client.put(url, params=params, data=data, json=json, headers=headers, timeout=timeout,
                                    files=files)
        return response


async def async_delete(url, headers=None, timeout=None, params=None):
    client_kwargs = get_httpx_client_kwargs()

    async with httpx.AsyncClient(**client_kwargs) as client:
        response = await client.delete(url, params=params, headers=headers, timeout=timeout)
        return response


async def async_get(url, params=None, headers=None, timeout=None):
    client_kwargs = get_httpx_client_kwargs()

    async with httpx.AsyncClient(**client_kwargs) as client:
        response = await client.get(url, params=params, headers=headers, timeout=timeout)
        return response


def find_in_list(lst, element):
    try:
        return lst[lst.index(element)]
    except ValueError:
        return None


def find_in_list_by_field(lst, field, element):
    for item in lst:
        if item[field] == element:
            return item

    return None


def extract_human_readable_filename(url: str) -> str:
    """
    Extract a human-readable filename from a URL, especially for Discord CDN URLs.
    
    Takes a URL like:
    https://cdn.discordapp.com/attachments/1334433356263194676/1335313374656860181/deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f.png?ex=679fb6fd&is=679e657d&hm=c58ae42143406364740aea7627649988d709ec47c86eacf9340a366a874bdd76&
    
    And returns: deborah_anime_girl.png
    
    Args:
        url (str): The URL to extract filename from
        
    Returns:
        str: Human-readable filename
    """
    try:
        # Parse URL and get the path
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        
        # Get filename from path
        filename = os.path.basename(path)
        
        if not filename:
            return "image.png"
            
        # Split filename and extension
        name_part, ext = os.path.splitext(filename)
        
        # If no extension, default to .png
        if not ext:
            ext = ".png"
            
        # For Discord CDN URLs, apply human-readable extraction
        if 'cdn.discordapp.com' in url or 'discord' in url.lower():
            return extract_discord_filename(name_part, ext)
            
        # For other URLs, try to clean up the filename
        return clean_filename(name_part, ext)
        
    except Exception:
        # Fallback to generic name if anything goes wrong
        return "image.png"


def extract_discord_filename(name_part: str, ext: str) -> str:
    """
    Extract human-readable name from Discord CDN filename.
    
    Example: deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f
    Returns: deborah_anime_girl
    """
    # Remove UUID-like patterns (hexadecimal with dashes)
    # Pattern for UUID: 8-4-4-4-12 hex digits
    name_part = re.sub(r'_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '', name_part)
    
    # Remove other hex patterns and numbers at the end
    name_part = re.sub(r'_[0-9a-fA-F]{6,}$', '', name_part)
    name_part = re.sub(r'_\d{10,}', '', name_part)  # Remove long numbers like timestamps
    
    # Split by underscores and keep meaningful words
    parts = name_part.split('_')
    meaningful_parts = []
    
    for part in parts:
        # Skip parts that are purely numeric or very short
        if len(part) < 2 or part.isdigit():
            continue
        # Skip parts that look like user IDs or codes (starts with letters followed by mostly numbers)
        # But keep common words that might have some numbers mixed in
        if re.match(r'^[a-zA-Z]+\d{3,}', part):  # Skip things like "user123", "id456" etc
            continue
        meaningful_parts.append(part)
    
    # Take first few meaningful parts
    result_parts = meaningful_parts[:3]  # Limit to avoid very long names
    
    if not result_parts:
        return f"image{ext}"
        
    result_name = '_'.join(result_parts)
    return f"{result_name}{ext}"


def clean_filename(name_part: str, ext: str) -> str:
    """
    Clean up a generic filename to make it more human-readable.
    """
    # Remove query parameters and fragments that might be in the name
    name_part = re.sub(r'[?#].*$', '', name_part)
    
    # Check for a meaningful prefix before a long hex sequence
    prefix_before_hex = re.match(r'^([a-zA-Z]{2,})[0-9a-fA-F]{16,}$', name_part)
    if prefix_before_hex:
        name_part = prefix_before_hex.group(1)
    else:
        # Remove very long hex sequences (16+ characters) from the end
        name_part = re.sub(r'[0-9a-fA-F]{16,}$', '', name_part)
    
    # If the name is empty or too short after cleaning, use a default
    if len(name_part) < 2:
        name_part = "image"
        
    return f"{name_part}{ext}"
