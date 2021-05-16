from typing import Container, Optional, Type

from pydantic import BaseModel, create_model

from alchemista.config import OrmConfig
from alchemista.field import fields_from


def sqlalchemy_to_pydantic(
    db_model: type, *, config: type = OrmConfig, exclude: Optional[Container[str]] = None
) -> Type[BaseModel]:
    fields = fields_from(db_model, exclude=exclude)
    return create_model(db_model.__name__, __config__=config, **fields)  # type: ignore
