import datetime as dt
import enum
import time

import pytest
from pydantic import ValidationError
from sqlalchemy import ARRAY, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import declarative_base

from alchemista import sqlalchemy_to_pydantic


def test_optional_behavior() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        defaulted_req_str = Column(String, default="default", nullable=False)
        opt_str = Column(String, default=None, nullable=True)
        req_str = Column(String, nullable=False)

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test)
    test = TestPydantic(id=1, req_str="str")

    # Assert
    assert getattr(test, "id") == 1
    assert getattr(test, "defaulted_req_str") == "default"
    assert getattr(test, "opt_str") is None
    assert getattr(test, "req_str") == "str"
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "defaulted_req_str": {
                "title": "Defaulted Req Str",
                "default": "default",
                "type": "string",
            },
            "opt_str": {"title": "Opt Str", "type": "string"},
            "req_str": {"title": "Req Str", "type": "string"},
        },
        "required": ["id", "req_str"],
    }

    with pytest.raises(ValidationError) as ex:
        TestPydantic(id=2, req_str="str", defaulted_req_str=None)
    errors = ex.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("defaulted_req_str",)
    assert errors[0]["msg"] == "none is not an allowed value"
    assert errors[0]["type"] == "type_error.none.not_allowed"


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
    assert getattr(test, "id") == 1
    assert getattr(test, "dynamic_column") == "dynamic default"
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
    assert getattr(test1, "id") == 1
    assert isinstance(getattr(test1, "datetime"), dt.datetime)
    assert getattr(test2, "id") == 2
    assert isinstance(getattr(test2, "datetime"), dt.datetime)
    assert getattr(test1, "datetime") < getattr(test2, "datetime")
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
    assert getattr(test, "id") == 1
    assert getattr(test, "number") == 0
    assert getattr(test, "number_mut") == 1
    setattr(test, "number_mut", 2)
    assert getattr(test, "number_mut") == 2
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "number": {"title": "Number", "type": "integer"},
            "number_mut": {"title": "Number Mut", "type": "integer"},
        },
        "required": ["id"],
    }

    with pytest.raises(TypeError):
        setattr(test, "number", 1)
    assert getattr(test, "number") == 0


def test_enum_schema() -> None:
    # Arrange
    Base = declarative_base()

    class Bool(str, enum.Enum):
        FALSE = "F"
        TRUE = "T"

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        boolean_default = Column(Enum(Bool), default=Bool.TRUE)
        boolean_not_native = Column(Enum(Bool, native_enum=False), default=Bool.TRUE)
        boolean_values = Column(
            Enum(Bool, values_callable=lambda enum: [item.value for item in enum]),
            default=Bool.TRUE,
        )
        boolean_values_not_native = Column(
            Enum(
                Bool,
                native=False,
                length=1,
                values_callable=lambda enum: [item.value for item in enum],
            ),
            default=Bool.TRUE,
        )

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test)
    test = TestPydantic(id=1)

    # Assert
    assert getattr(test, "id") == 1
    assert getattr(test, "boolean_default") == Bool.TRUE
    assert getattr(test, "boolean_not_native") == Bool.TRUE
    assert getattr(test, "boolean_values") == Bool.TRUE
    assert getattr(test, "boolean_values_not_native") == Bool.TRUE
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "boolean_default": {
                "default": Bool.TRUE,
                "allOf": [{"$ref": "#/definitions/Bool"}],
            },
            "boolean_not_native": {
                "default": Bool.TRUE,
                "allOf": [{"$ref": "#/definitions/Bool"}],
            },
            "boolean_values": {
                "default": Bool.TRUE,
                "allOf": [{"$ref": "#/definitions/Bool"}],
            },
            "boolean_values_not_native": {
                "default": Bool.TRUE,
                "allOf": [{"$ref": "#/definitions/Bool"}],
            },
        },
        "required": ["id"],
        "definitions": {
            "Bool": {
                "title": "Bool",
                "description": "An enumeration.",
                "enum": ["F", "T"],
                "type": "string",
            }
        },
    }


def test_all_pydantic_attributes_from_info() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        ge_le = Column(Integer, info=dict(ge=0, le=10))
        gt_lt = Column(Integer, info=dict(gt=0, lt=10))
        items = Column(ARRAY(item_type=Text), info=dict(min_items=0, max_items=2))
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
    assert getattr(test, "id") == 1
    assert getattr(test, "ge_le") == 0
    assert getattr(test, "gt_lt") == 1
    assert getattr(test, "items") == []
    assert getattr(test, "multiple") == 2
    assert getattr(test, "string") == "txt"
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "ge_le": {"title": "Ge Le", "minimum": 0, "maximum": 10, "type": "integer"},
            "gt_lt": {"title": "Gt Lt", "exclusiveMinimum": 0, "exclusiveMaximum": 10, "type": "integer"},
            "items": {"title": "Items", "minItems": 0, "maxItems": 2, "type": "array", "items": {"type": "string"}},
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


def test_keyed_column_schema() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        text = Column(String(64), key="string")

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test)
    test = TestPydantic(id=1, text="txt")

    # Assert
    assert getattr(test, "id") == 1
    assert getattr(test, "text") == "txt"
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "text": {"title": "Text", "maxLength": 64, "type": "string"},
            "id": {"title": "Id", "type": "integer"},
        },
        "required": ["id"],
    }


def test_exclude_removes_fields_from_generated_model() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number = Column(Integer)

    # Act
    TestPydantic = sqlalchemy_to_pydantic(Test, exclude={"number"})

    # Assert
    test = TestPydantic(id=1)
    assert getattr(test, "id") == 1
    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
        },
        "required": ["id"],
    }
