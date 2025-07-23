import httpx
import config


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
