from typing import Container, Optional, Type

from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty

from alchemista.field import infer_python_type, make_field


class OrmConfig(BaseConfig):
    orm_mode = True


def sqlalchemy_to_pydantic(
    db_model: type, *, config: type = OrmConfig, exclude: Optional[Container[str]] = None
) -> Type[BaseModel]:
    if exclude is None:
        exclude = []
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty) and attr.columns:
            name = attr.key
            if name in exclude:
                continue
            column = attr.columns[0]
            python_type = infer_python_type(column)
            field = make_field(column)
            fields[name] = (python_type, field)
    pydantic_model = create_model(db_model.__name__, __config__=config, **fields)  # type: ignore
    return pydantic_model
