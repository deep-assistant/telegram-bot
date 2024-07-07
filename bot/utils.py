from enum import Enum


def include(arr: [str], value: str) -> bool:
    return len(list(filter(lambda x: value.startswith(x), arr))) > 0


def get_user_name(user_id: str):
    return str(user_id)


def divide_into_chunks(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
