from pydantic import BaseConfig


class OrmConfig(BaseConfig):
    orm_mode = True
