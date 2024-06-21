from enum import Enum


def include(arr: [str], value: str) -> bool:
    return len(list(filter(lambda x: value.startswith(x), arr))) > 0


def get_user_name(user_id: str, model: Enum):
    return str(user_id) + model.value + "1"
