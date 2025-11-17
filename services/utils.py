import httpx
import config
import asyncio


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


# ========== Health Check для локального API ==========

async def check_api_health(url: str, max_retries: int = 3, timeout: float = 5.0) -> bool:
    """
    Проверка доступности API
    
    Args:
        url: Base URL API (например, http://localhost:8000)
        max_retries: Количество попыток
        timeout: Таймаут на каждую попытку
        
    Returns:
        bool: True если API доступен, False иначе
    """
    health_endpoint = f"{url}/health"  # Предполагаем что есть /health endpoint
    
    for attempt in range(max_retries):
        try:
            response = await async_get(health_endpoint, timeout=timeout)
            if response.status_code == 200:
                print(f"[Health Check] ✅ API доступен: {url}")
                return True
        except httpx.ConnectError:
            print(f"[Health Check] ❌ Попытка {attempt + 1}/{max_retries}: Не удалось подключиться к {url}")
        except httpx.TimeoutException:
            print(f"[Health Check] ❌ Попытка {attempt + 1}/{max_retries}: Таймаут при подключении к {url}")
        except Exception as e:
            print(f"[Health Check] ❌ Попытка {attempt + 1}/{max_retries}: {type(e).__name__}: {str(e)}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2)  # Пауза перед следующей попыткой
    
    print(f"[Health Check] ❌ API недоступен после {max_retries} попыток: {url}")
    return False


async def wait_for_api(url: str, max_wait_time: int = 60) -> bool:
    """
    Ждет пока API станет доступным
    
    Args:
        url: Base URL API
        max_wait_time: Максимальное время ожидания в секундах
        
    Returns:
        bool: True если API стал доступен, False если истекло время
    """
    print(f"[Health Check] Ожидание доступности API: {url}")
    start_time = asyncio.get_event_loop().time()
    
    while (asyncio.get_event_loop().time() - start_time) < max_wait_time:
        if await check_api_health(url, max_retries=1, timeout=3.0):
            return True
        await asyncio.sleep(5)  # Проверяем каждые 5 секунд
    
    return False
