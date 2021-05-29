# Alchemista

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/ggabriel96/alchemista/branch/main/graph/badge.svg?token=MYXKIH09FJ)](https://codecov.io/gh/ggabriel96/alchemista)

Tools to generate Pydantic models from SQLAlchemy models.

Still experimental.

## Installation

Alchemista is [available in PyPI](https://pypi.org/project/alchemista/).
To install it with `pip`, run:


```shell
pip install alchemista
```

## Usage

Simply call the `model_from` function with a SQLAlchemy model.
Each `Column` in its definition will result in an attribute of the generated model via the Pydantic `Field` function.

For example, a SQLAlchemy model like the following

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class PersonDB(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    age = Column(Integer, default=0, nullable=False, doc="Age in years")
    name = Column(String(128), nullable=False, doc="Full name")
```

could have a generated Pydantic model via

```python
from alchemista import model_from

Person = model_from(PersonDB)
```

and would result in a Pydantic model equivalent to

```python
from pydantic import BaseModel, Field


class Person(BaseModel):
    id: int
    age: int = Field(0, description="Age in years")
    name: str = Field(..., max_length=128, description="Full name")

    class Config:
        orm_mode = True
```

Note that the string length from the column definition was sufficient to add a `max_length` constraint.
Additionally, by default, the generated model will have `orm_mode=True`.
That can be customized via the `__config__` keyword argument.

There is also an `exclude` keyword argument that accepts a set of field names to _not_ include in the generated model,
and an `include` keyword argument accepts a set of field names to _do_ include in the generated model.
However, they are mutually exclusive and cannot be used together.

This example is available in a short executable form in the [`examples/`](examples/) directory.

## `Field` arguments and `info`

Currently, the type, default value (either scalar or callable), and the description (from the `doc` attribute) are
extracted directly from the `Column` definition.
However, except for the type, all of them can be overridden via the `info` dictionary attribute.
All other custom arguments to the `Field` function are specified there too.
The supported keys are listed in `alchemista.field.Info`.

**Everything specified in `info` is preferred from what has been extracted from `Column`**.
This means that the default value and the description can be **overridden** if so desired.
Also, similarly to using Pydantic directly, `default` and `default_factory` are mutually-exclusive,
so they cannot be used together.
Use `default_factory` if the default value comes from calling a function (without any arguments).

For example, in the case above,

```python
name = Column(String(128), nullable=False, doc="Full name", info=dict(description=None, max_length=64))
```

would instead result in

```python
name: str = Field(..., max_length=64)
```

## `fields_from` and `model_from`

The `fields_from` function is the function that actually inspects the SQLAlchemy model and builds a dictionary
    in a format that can be used to generate a Pydantic model.
So `model_from` is just a shortcut for calling `fields_from` and then `pydantic.create_model`.
The model name that `model_from` sets is `db_model.__name__`.

If desired, or extra control is needed, `pydantic.create_model` can be used directly, in conjunction with `fields_from`.
This allows the customization of the name of the model that will be created and the specification of other
    `create_model` arguments, like `__base__` and `__validators__` (`model_from` currently only accepts `__config__`).

For example:

```python
from alchemista import fields_from
from pydantic import create_model


MyModel = create_model("MyModel", **fields_from(DBModel))
```

## `transform`

Both `fields_from` and `model_from` have a `transform` argument.
It is a callable used to transform the fields before generating a Pydantic model.
The provided transformation functions are in the `func` module.
By default, the `transform` argument is set to `func.unchanged`, which, as the name implies, does nothing.

The other provided transformation function is `func.nonify`, which makes all fields optional (if they weren't already)
    and nullable and sets the default value to `None`.
This is useful when some kind of "input model" is desired.
For example, the database model might have an auto-generated primary key, and some other columns with default values.
When updating an entity of this model, one wouldn't want to receive the primary key as an update candidate (which can
    be solved using the `exclude` argument) and probably wouldn't want the fields with default values to actually have
    these values, since the update is meant to change only what the user asked to update.

For example:

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from alchemista import model_from
from alchemista.func import nonify


Base = declarative_base()

class PersonDB(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    age = Column(Integer, default=0, nullable=False, doc="Age in years")
    name = Column(String(128), nullable=False, doc="Full name")


PersonInput = model_from(PersonDB, exclude={"id"}, transform=nonify)
```

The model `PersonInput` is equivalent to the hand-written version below:

```python
from typing import Optional

from pydantic import BaseModel, Field


class PersonInput(BaseModel):
    age: Optional[int] = Field(None, description="Age in years")
    name: Optional[str] = Field(None, max_length=128, description="Full name")

    class Config:
        orm_mode = True
```

Note that both `age` and `name` weren't originally nullable (`Optional`, in Python) and the name was required (age
    wasn't because it has a default value).
Now, both fields are nullable and their default value is `None`.

### User-defined transformations

You can also create your own transformation functions.
The expected signature is as follows:

```python
from typing import Tuple

from pydantic.fields import FieldInfo

def transformation(name: str, python_type: type, field: FieldInfo) -> Tuple[type, FieldInfo]:
    pass
```

Where `name` is the name of the field currently being created, `python_type` is its Python type, and `field` is its full
    Pydantic field specification.
The return type is a tuple of the Python type and the field specification.
These two can be changed freely (the name can't).

## License

This project is licensed under the terms of the MIT license.
