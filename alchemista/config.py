from pydantic import BaseConfig, Extra


class OrmConfig(BaseConfig):
    orm_mode = True


class CRUDConfig(BaseConfig):
    # we generally don't want CRUD input to be empty, mutable, or have unexpected fields
    allow_mutation = False
    extra = Extra.forbid
