import httpx
import config
import asyncio
import logging


def get_httpx_client_kwargs():
    """Get common httpx client configuration from config."""
    kwargs = {
        'timeout': httpx.Timeout(120.0, connect=30.0),  # 120s total, 30s connect timeout
        'limits': httpx.Limits(max_keepalive_connections=20, max_connections=100),
        'follow_redirects': True,
    }

    if getattr(config, 'HTTPX_DISABLE_SSL_VERIFY', False):
        kwargs['verify'] = False

    return kwargs


async def _retry_request(request_func, max_retries: int = 3):
    """Helper function to retry HTTP requests with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return await request_func()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadTimeout, httpx.WriteTimeout, ConnectionResetError) as e:
            if attempt == max_retries:
                logging.error(f"HTTP request failed after {max_retries + 1} attempts: {e}")
                raise
            
            wait_time = 2 ** attempt
            logging.warning(f"HTTP request attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            logging.error(f"Unexpected error during HTTP request: {e}")
            raise


async def async_post(url, data=None, json=None, headers=None, timeout=None, files=None, params=None):
    client_kwargs = get_httpx_client_kwargs()
    
    # Override timeout if specified
    if timeout is not None:
        client_kwargs['timeout'] = timeout

    async def _make_request():
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.post(url, params=params, data=data, json=json, headers=headers, 
                                       files=files)
            return response
    
    return await _retry_request(_make_request)


async def async_put(url, data=None, json=None, headers=None, timeout=None, files=None, params=None):
    client_kwargs = get_httpx_client_kwargs()
    
    # Override timeout if specified
    if timeout is not None:
        client_kwargs['timeout'] = timeout

    async def _make_request():
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.put(url, params=params, data=data, json=json, headers=headers,
                                      files=files)
            return response
    
    return await _retry_request(_make_request)


async def async_delete(url, headers=None, timeout=None, params=None):
    client_kwargs = get_httpx_client_kwargs()
    
    # Override timeout if specified
    if timeout is not None:
        client_kwargs['timeout'] = timeout

    async def _make_request():
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.delete(url, params=params, headers=headers)
            return response
    
    return await _retry_request(_make_request)


async def async_get(url, params=None, headers=None, timeout=None):
    client_kwargs = get_httpx_client_kwargs()
    
    # Override timeout if specified
    if timeout is not None:
        client_kwargs['timeout'] = timeout

    async def _make_request():
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.get(url, params=params, headers=headers)
            return response
    
    return await _retry_request(_make_request)


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
