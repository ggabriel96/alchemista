from typing import Container, Optional, Type, cast

from pydantic import BaseConfig, BaseModel, create_model

from alchemista.config import OrmConfig
from alchemista.field import fields_from


def model_from(
    db_model: type,
    *,
    exclude: Optional[Container[str]] = None,
    include: Optional[Container[str]] = None,
    __config__: Type[BaseConfig] = OrmConfig,
) -> Type[BaseModel]:
    fields = fields_from(db_model, exclude=exclude, include=include)
    return cast(
        Type[BaseModel],
        create_model(db_model.__name__, __config__=__config__, **fields),  # type: ignore[arg-type]
    )
