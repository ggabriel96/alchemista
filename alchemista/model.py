from typing import Callable, Container, Optional, Tuple, Type, cast

from pydantic import BaseConfig, BaseModel, create_model
from pydantic.fields import FieldInfo

from alchemista import func
from alchemista.config import OrmConfig
from alchemista.field import fields_from


def model_from(
    db_model: type,
    *,
    exclude: Optional[Container[str]] = None,
    include: Optional[Container[str]] = None,
    transform: Callable[[str, type, FieldInfo], Tuple[type, FieldInfo]] = func.unchanged,
    __config__: Type[BaseConfig] = OrmConfig,
) -> Type[BaseModel]:
    fields = fields_from(db_model, exclude=exclude, include=include, transform=transform)
    return cast(
        Type[BaseModel],
        create_model(db_model.__name__, __config__=__config__, **fields),  # type: ignore[arg-type]
    )
