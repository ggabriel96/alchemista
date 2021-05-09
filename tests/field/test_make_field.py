import time
import datetime as dt

import pytest
from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

from pydantic_sqlalchemy import sqlalchemy_to_pydantic


def test_default_comes_from_column_definition() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        column = Column(String, default="default")

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test)
    test = TestPydantic(id=1)

    # Assert
    assert test.id == 1
    assert test.column == "default"
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "column": {"title": "Column", "default": "default", "type": "string"},
        },
        "required": ["id"],
    }


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


def test_all_pydantic_attributes_from_info() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        ge_le = Column(Integer, info=dict(ge=0, le=10))
        gt_lt = Column(Integer, info=dict(gt=0, lt=10))
        items = Column(ARRAY(item_type=str), info=dict(min_items=0, max_items=2))
        multiple = Column(Integer, info=dict(multiple_of=2))
        string = Column(
            Text,
            default="",
            nullable=False,
            info=dict(
                alias="text",
                const="",
                description="Some string",
                example="Example",
                max_length=64,
                min_length=0,
                regex=r"\w+",
                title="SomeString",
            ),
        )

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test)
    test = TestPydantic(id=1, ge_le=0, gt_lt=1, items=[], multiple=2, text="txt")

    # Assert
    assert test.id == 1
    assert test.ge_le == 0
    assert test.gt_lt == 1
    assert test.items == []
    assert test.multiple == 2
    assert test.string == "txt"
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "ge_le": {"title": "Ge Le", "minimum": 0, "maximum": 10, "type": "integer"},
            "gt_lt": {
                "title": "Gt Lt",
                "exclusiveMinimum": 0,
                "exclusiveMaximum": 10,
                "type": "integer",
            },
            "items": {
                "title": "Items",
                "minItems": 0,
                "maxItems": 2,
                "type": "array",
                "items": {},
            },
            "multiple": {"title": "Multiple", "multipleOf": 2, "type": "integer"},
            "text": {
                "title": "SomeString",
                "description": "Some string",
                "default": "",
                "maxLength": 64,
                "minLength": 0,
                "pattern": "\\w+",
                "example": "Example",
                "type": "string",
            },
        },
        "required": ["id"],
    }
