def include(arr: [str], value: str) -> bool:
    return len(list(filter(lambda x: x == value, arr))) > 0
