from pydantic import BaseConfig, Extra


class OrmConfig(BaseConfig):
    orm_mode = True


class CRUDConfig(BaseConfig):
    allow_mutation = True
    extra = Extra.forbid
