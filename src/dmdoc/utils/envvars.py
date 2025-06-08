import os
from typing import Any


def resolve_any(_object: Any) -> Any:
    if isinstance(_object, str):
        return resolve_str(_object)
    elif isinstance(_object, list):
        return resolve_list(_object)
    elif isinstance(_object, dict):
        return resolve_dict(_object)
    else:
        return _object


def resolve_list(_list: list) -> list:
    return [
        resolve_any(item)
        for item in _list
    ]


def resolve_dict(_dict: dict) -> dict:
    return {
        k: resolve_any(v)
        for k, v in _dict.items()
    }


def resolve_str(_str: str) -> str:
    return os.path.expandvars(_str)
