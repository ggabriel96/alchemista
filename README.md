# Alchemista

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/ggabriel96/alchemista/branch/main/graph/badge.svg?token=MYXKIH09FJ)](https://codecov.io/gh/ggabriel96/alchemista)

Tools to generate Pydantic models from SQLAlchemy models.

Still experimental.

## How to use

Quick example:

```python
from alchemista import sqlalchemy_to_pydantic
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()
engine = create_engine("sqlite://", echo=True)


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    name = Column(String, nullable=False)


PersonPydantic = sqlalchemy_to_pydantic(Person)


Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)

person = PersonPydantic.construct(name="Someone", age=25)
with SessionMaker.begin() as session:
    session.add(Person(**person.dict()))

with SessionMaker.begin() as session:
    person_db = session.execute(select(Person)).scalar_one()
    person = PersonPydantic.from_orm(person_db)
    print(person)
```

## License

This project is licensed under the terms of the MIT license.
