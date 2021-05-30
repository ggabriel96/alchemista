from typing import Any, Callable, Container, Dict, List, Optional, Tuple, cast

from pydantic import Field
from pydantic.fields import FieldInfo
from sqlalchemy import Column, Enum, inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.types import TypeEngine
from typing_extensions import TypedDict


class Info(TypedDict, total=False):
    alias: str
    allow_mutation: bool
    const: Any
    default: Any
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
    except (AttributeError, NotImplementedError) as ex:
        raise RuntimeError(
            f"Could not infer the Python type for {column}."
            " Check if the column type has a `python_type` in it or in `impl`"
        ) from ex

    if python_type is list and hasattr(column.type, "item_type"):
        item_type = _extract_python_type(column.type.item_type)
        if column.nullable:
            return Optional[List[item_type]]  # type: ignore[valid-type, return-value]
        return List[item_type]  # type: ignore[valid-type]

    return python_type if not column.nullable else Optional[python_type]  # type: ignore[return-value]


def _get_default_scalar(column: Column) -> Any:  # type: ignore[type-arg]
    if column.default and column.default.is_scalar:
        return column.default.arg
    if column.nullable is False:
        return ...
    return None


def _maybe_set_max_length_from_column(field_kwargs: Info, column: Column) -> None:  # type: ignore[type-arg]
    # some types have a length in the backend, but setting that interferes with the model generation
    # maybe we should list the types that we *should set* the length, instead of *not set* the length?
    if not isinstance(column.type, Enum):
        sa_type_length = getattr(column.type, "length", None)
        if sa_type_length is not None:
            field_kwargs["max_length"] = sa_type_length


def make_field(column: Column) -> FieldInfo:  # type: ignore[type-arg]
    info = Info()
    if column.info:
        for key in Info.__annotations__.keys():
            if key in column.info:
                info[key] = column.info[key]  # type: ignore[misc]

    if "max_length" not in info:
        _maybe_set_max_length_from_column(info, column)

    if "description" not in info and column.doc:
        info["description"] = column.doc

    if "default" in info and "default_factory" in info:
        raise ValueError(
            f"Both `default` and `default_factory` were specified in info of column `{column.name}`."
            " These two attributes are mutually-exclusive"
        )

    if "default" not in info and "default_factory" not in info and column.default and column.default.is_callable:
        return cast(FieldInfo, Field(**info, default_factory=column.default.arg.__wrapped__))  # type: ignore[misc]

    if "default_factory" in info:
        return cast(FieldInfo, Field(**info))

    # pop `default` because it is not a keyword argument of `Field`
    default = info.pop("default") if "default" in info else _get_default_scalar(column)
    return cast(FieldInfo, Field(default, **info))  # type: ignore[misc]


def fields_from(
    db_model: type,
    *,
    exclude: Optional[Container[str]] = None,
    include: Optional[Container[str]] = None,
) -> Dict[str, Tuple[type, FieldInfo]]:
    if exclude and include:
        raise ValueError("`exclude` and `include` are mutually-exclusive")
    mapper = inspect(db_model)
    candidate_attrs = mapper.attrs
    if exclude:
        candidate_attrs = (attr for attr in mapper.attrs if attr.key not in exclude)
    elif include:
        candidate_attrs = (attr for attr in mapper.attrs if attr.key in include)
    fields = {}
    for attr in candidate_attrs:
        if isinstance(attr, ColumnProperty) and attr.columns:
            name = attr.key
            column = attr.columns[0]
            python_type = infer_python_type(column)
            field = make_field(column)
            fields[name] = (python_type, field)
    return fields
