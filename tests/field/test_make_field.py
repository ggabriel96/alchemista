import time
import datetime as dt

import pytest
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from pydantic_sqlalchemy.field import make_field


def test_default_comes_from_column_definition() -> None:
    # Arrange
    column = Column("col", String, default="default")

    # Act
    field = make_field(column)

    # Assert
    assert field.default == "default"


def test_lambda_as_default_factory() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        dynamic_column = Column(String, default=lambda: "dynamic default")

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test)
    test = TestPydantic(id=1)

    # Assert
    assert test.id == 1
    assert test.dynamic_column == "dynamic default"
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "dynamic_column": {"title": "Dynamic Column", "type": "string"},
        },
        "required": ["id"],
    }


def test_datetime_now_as_default_factory() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        datetime = Column(DateTime, default=dt.datetime.now)

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test)
    test1 = TestPydantic(id=1)
    time.sleep(0.1)
    test2 = TestPydantic(id=2)

    # Assert
    assert test1.id == 1
    assert isinstance(test1.datetime, dt.datetime)
    assert test2.id == 2
    assert isinstance(test2.datetime, dt.datetime)
    assert test1.datetime < test2.datetime
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "datetime": {"title": "Datetime", "type": "string", "format": "date-time"},
        },
        "required": ["id"],
    }


def test_allow_mutation() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number = Column(Integer, info=dict(allow_mutation=False))
        number_mut = Column(Integer, info=dict(allow_mutation=True))

    class ValidateAssignment:
        validate_assignment = True

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test, config=ValidateAssignment)
    test = TestPydantic(id=1, number=0, number_mut=1)

    # Assert
    assert test.id == 1
    assert test.number == 0
    assert test.number_mut == 1
    test.number_mut = 2
    assert test.number_mut == 2
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "number": {"title": "Number", "allow_mutation": False, "type": "integer"},
            "number_mut": {
                "title": "Number Mut",
                "allow_mutation": True,
                "type": "integer",
            },
        },
        "required": ["id"],
    }

    with pytest.raises(TypeError):
        test.number = 1
    assert test.number == 0
