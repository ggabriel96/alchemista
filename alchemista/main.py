from typing import Container, Optional, Type

from deprecated import deprecated
from pydantic import BaseConfig, BaseModel

from alchemista.config import OrmConfig
from alchemista.model import model_from


@deprecated("Migrate to directly using `model_from`", version="0.2.0")
def sqlalchemy_to_pydantic(
    db_model: type,
    *,
    config: Type[BaseConfig] = OrmConfig,
    exclude: Optional[Container[str]] = None,
) -> Type[BaseModel]:
    return model_from(db_model, __config__=config, exclude=exclude)
