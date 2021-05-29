from typing import Optional, Tuple

from pydantic.fields import FieldInfo

from alchemista.typing import is_optional


def unchanged(_: str, python_type: type, field: FieldInfo) -> Tuple[type, FieldInfo]:
    return python_type, field


def nonify(_: str, python_type: type, field: FieldInfo) -> Tuple[type, FieldInfo]:
    """Wrap `python_type` in `typing.Optional` if it wasn't originally,
    while also setting the default value of `field` to None."""
    field.const = field.default = field.default_factory = None
    if is_optional(python_type):
        return python_type, field
    return Optional[python_type], field  # type: ignore[return-value]
