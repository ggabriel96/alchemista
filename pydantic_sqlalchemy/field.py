from numbers import Number
from typing import Any, Callable, Optional

from pydantic import Field
from sqlalchemy import Column
from typing_extensions import TypedDict


class FieldKwargs(TypedDict, total=False):
    alias: Optional[str]
    allow_mutation: Optional[bool]
    const: Optional[Any]
    default_factory: Optional[Callable[[], Any]]
    description: Optional[str]
    example: Optional[str]
    ge: Optional[Number]
    gt: Optional[Number]
    le: Optional[Number]
    lt: Optional[Number]
    max_items: Optional[int]
    max_length: Optional[int]
    min_items: Optional[int]
    min_length: Optional[int]
    multiple_of: Optional[Number]
    regex: Optional[str]
    title: Optional[str]


def infer_python_type(column: Column) -> Optional[type]:
    try:
        if hasattr(column.type, "impl"):
            if hasattr(column.type.impl, "python_type"):
                return column.type.impl.python_type
        elif hasattr(column.type, "python_type"):
            return column.type.python_type
    except NotImplementedError as nie:
        raise RuntimeError(f"Could not infer `python_type` for {column}") from nie


def _get_default(column: Column) -> Any:
    if column.default:
        # can't join these `if` or else an optional field will end without a default value
        if column.default.is_scalar:
            return column.default.arg
    elif column.nullable is False:
        return ...
    return None


def make_field(column: Column) -> Field:
    field_kwargs = FieldKwargs()
    for key in FieldKwargs.__annotations__.keys():
        if key in column.info:
            field_kwargs[key] = column.info[key]
    default = _get_default(column)
    return Field(default, **field_kwargs)
