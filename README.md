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

Simply call the `sqlalchemy_to_pydantic` function with a SQLAlchemy model.
Each `Column` in its definition will result in an attribute of the generated model via the Pydantic `Field` function.
The supported attributes are listed in `alchemista.field.Info`.
Some of them can be extracted from `Column` attributes directly, like the default value and the description.

For example, a SQLAlchemy model like the following

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    age = Column(Integer, default=0, nullable=False, doc="Age in years")
    name = Column(String(128), nullable=False, doc="Full name")
```

could have a generated Pydantic model via

```python
from alchemista import sqlalchemy_to_pydantic

PersonPydantic = sqlalchemy_to_pydantic(Person)
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
That can be customized via the `config` keyword argument.
There is also an `exclude` keyword argument that accepts a set of field names to _not_ include in the generated model.

### The `info` dictionary

All attributes, except for a default scalar value, can be specified via the `info` dictionary of `Column`.
This includes what is inferred from column attributes directly, like the description shown previously.
Everything specified in `info` is preferred from what is inferred.

For example, in the case above,

```python
name = Column(String(128), nullable=False, doc="Full name", info=dict(description=None, max_length=64))
```

would instead result in

```python
name: str = Field(..., max_length=64)
```

## License

This project is licensed under the terms of the MIT license.
