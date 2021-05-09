from numbers import Number
from typing import Any, Callable, List, Optional, TypeVar

from pydantic import Field
from sqlalchemy import Column, Enum
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
        # the `python_type` seems to always be an @property-decorated method,
        # so only checking its existence is not enough
        python_type = column.type.python_type
    except (AttributeError, NotImplementedError):
        try:
            python_type = column.type.impl.python_type
        except (AttributeError, NotImplementedError):
            raise RuntimeError(
                f"Could not infer the Python type for {column}."
                " Check if the column type has a `python_type` in it or in `impl`"
            )

    if python_type is list and hasattr(column.type, "item_type"):
        # can't use `column.type.item_type` directly
        ItemType = TypeVar("ItemType", bound=column.type.item_type)
        return List[ItemType]

    return python_type


def _get_default(column: Column) -> Any:
    if column.default:
        # can't join these `if` or else an optional field will end without a default value
        if column.default.is_scalar:
            return column.default.arg
    elif column.nullable is False:
        return ...
    return None


def _set_max_length_from_column_if_present(field_kwargs: FieldKwargs, column: Column) -> None:
    # some types have a length in the backend, but setting that interferes with the model generation
    # maybe we should list the types that we *should set* the length, instead of *not set* the length?
    if not isinstance(column.type, Enum):
        sa_type_length = getattr(column.type, "length", None)
        if sa_type_length is not None:
            info_max_length = field_kwargs.get("max_length")
            if info_max_length and info_max_length != sa_type_length:
                raise ValueError(
                    f"max_length ({info_max_length}) differs from length set for column type ({sa_type_length})."
                    " Either remove max_length from info (preferred) or set them to equal values"
                )
            field_kwargs["max_length"] = sa_type_length


def make_field(column: Column) -> Field:
    field_kwargs = FieldKwargs()
    for key in FieldKwargs.__annotations__.keys():
        if key in column.info:
            field_kwargs[key] = column.info[key]

    _set_max_length_from_column_if_present(field_kwargs, column)

    if "default_factory" not in field_kwargs and column.default and column.default.is_callable:
        field_kwargs["default_factory"] = column.default.arg.__wrapped__
        return Field(**field_kwargs)

    default = _get_default(column)
    return Field(default, **field_kwargs)
