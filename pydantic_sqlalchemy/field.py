from typing import Any, Callable, List, cast

from pydantic import Field
from pydantic.fields import FieldInfo
from sqlalchemy import Column, Enum
from sqlalchemy.types import TypeEngine
from typing_extensions import TypedDict


class FieldKwargs(TypedDict, total=False):
    alias: str
    allow_mutation: bool
    const: Any
    default_factory: Callable[[], Any]
    description: str
    example: str
    ge: float
    gt: float
    le: float
    lt: float
    max_items: int
    max_length: int
    min_items: int
    min_length: int
    multiple_of: float
    regex: str
    title: str


def _extract_python_type(type_engine: TypeEngine) -> type:  # type: ignore[type-arg]
    try:
        # the `python_type` seems to always be a @property-decorated method,
        # so only checking its existence is not enough
        return type_engine.python_type
    except (AttributeError, NotImplementedError):
        return cast(type, type_engine.impl.python_type)  # type: ignore[attr-defined]


def infer_python_type(column: Column) -> type:  # type: ignore[type-arg]
    try:
        python_type = _extract_python_type(column.type)
    except (AttributeError, NotImplementedError):
        raise RuntimeError(
            f"Could not infer the Python type for {column}."
            " Check if the column type has a `python_type` in it or in `impl`"
        )

    if python_type is list and hasattr(column.type, "item_type"):
        item_type = _extract_python_type(column.type.item_type)
        return List[item_type]  # type: ignore[valid-type]

    return python_type


def _get_default_scalar(column: Column) -> Any:  # type: ignore[type-arg]
    if column.default and column.default.is_scalar:
        return column.default.arg
    if column.nullable is False:
        return ...
    return None


def _set_max_length_from_column_if_present(field_kwargs: FieldKwargs, column: Column) -> None:  # type: ignore[type-arg]
    # some types have a length in the backend, but setting that interferes with the model generation
    # maybe we should list the types that we *should set* the length, instead of *not set* the length?
    if not isinstance(column.type, Enum):
        sa_type_length = getattr(column.type, "length", None)
        if sa_type_length is not None:
            info_max_length = field_kwargs.get("max_length")
            if info_max_length and info_max_length != sa_type_length:
                raise ValueError(
                    f"max_length ({info_max_length}) of `info` differs from length set in column type"
                    f" ({sa_type_length}) on column `{column.name}`. Either remove max_length from `info` (preferred)"
                    " or set them to equal values"
                )
            field_kwargs["max_length"] = sa_type_length


def make_field(column: Column) -> FieldInfo:  # type: ignore[type-arg]
    field_kwargs = FieldKwargs()
    if column.info:
        for key in FieldKwargs.__annotations__.keys():
            if key in column.info:
                field_kwargs[key] = column.info[key]  # type: ignore[misc]

    _set_max_length_from_column_if_present(field_kwargs, column)

    if "description" not in field_kwargs and column.doc:
        field_kwargs["description"] = column.doc

    if "default_factory" not in field_kwargs and column.default and column.default.is_callable:
        field_kwargs["default_factory"] = column.default.arg.__wrapped__
        return cast(FieldInfo, Field(**field_kwargs))

    default = _get_default_scalar(column)
    return cast(FieldInfo, Field(default, **field_kwargs))
