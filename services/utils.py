import httpx


async def async_post(url, data=None, json=None, headers=None, timeout=None, files=None):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, json=json, headers=headers, timeout=timeout, files=files)
        return response


async def async_get(url, params=None, headers=None, timeout=None):
    async with httpx.AsyncClient() as client:
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
