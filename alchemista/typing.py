from typing import Union, get_args, get_origin


def is_optional(python_type: type) -> bool:
    return get_origin(python_type) is Union and type(None) in get_args(python_type)
