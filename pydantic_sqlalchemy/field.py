from numbers import Number
from typing import Any, Callable, Optional

from pydantic import Field
from sqlalchemy import Column
from typing_extensions import TypedDict


class FieldKwargs(TypedDict):
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


def make_field(column: Column) -> Field:
    field_kwargs = FieldKwargs(
        alias=column.info.get("alias"),
        allow_mutation=column.info.get("allow_mutation"),
        const=column.info.get("const"),
        default_factory=column.info.get("default_factory"),
        description=column.info.get("description"),
        example=column.info.get("example"),
        ge=column.info.get("ge"),
        gt=column.info.get("gt"),
        le=column.info.get("le"),
        lt=column.info.get("lt"),
        max_items=column.info.get("max_items"),
        max_length=column.info.get("max_length"),
        min_items=column.info.get("min_items"),
        min_length=column.info.get("min_length"),
        multiple_of=column.info.get("multiple_of"),
        regex=column.info.get("regex"),
        title=column.info.get("title"),
    )
    default = column.info.get("default")
    if default is None:
        if column.default is not None:
            default = column.default
        elif column.nullable is False:
            default = ...
    return Field(default, **field_kwargs)
