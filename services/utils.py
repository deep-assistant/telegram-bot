import httpx


async def async_post(url, json, headers):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json, headers=headers)
        return response


async def async_get(url, params=None, headers=None, timeout=None):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=timeout)
        return response
