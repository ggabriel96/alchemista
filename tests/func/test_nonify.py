from typing import Optional

import pydantic
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

from alchemista import fields_from, model_from
from alchemista.func import nonify


def test_default_and_default_factory_and_const_become_none() -> None:
    # Arrange
    Base = declarative_base()  # pylint: disable=invalid-name

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number1 = Column(Integer, default=1, nullable=False, info=dict(const=1))
        number2 = Column(Integer, default=lambda: 2, nullable=False, info=dict(const=2))

    # Act
    fields = fields_from(Test, transform=nonify)
    TestPydantic = pydantic.create_model(  # pylint: disable=invalid-name
        Test.__name__, **fields  # type: ignore[arg-type, var-annotated]
    )
    test = TestPydantic()

    # Assert
    assert len(fields) == 3
    assert "id" in fields
    assert "number1" in fields
    assert "number2" in fields
    assert fields["id"][0] is Optional[int]
    assert fields["id"][1].const is None
    assert fields["id"][1].default is None
    assert fields["id"][1].default_factory is None
    assert fields["number1"][0] is Optional[int]
    assert fields["number1"][1].const is None
    assert fields["number1"][1].default is None
    assert fields["number1"][1].default_factory is None
    assert fields["number2"][0] is Optional[int]
    assert fields["number2"][1].const is None
    assert fields["number2"][1].default is None
    assert fields["number2"][1].default_factory is None

    assert getattr(test, "id", 3) is None
    assert getattr(test, "number1", 3) is None
    assert getattr(test, "number2", 3) is None

    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "number1": {"title": "Number1", "type": "integer"},
            "number2": {"title": "Number2", "type": "integer"},
        },
    }


def test_all_columns_become_optional_and_nullable_with_none_as_default() -> None:
    # Arrange
    Base = declarative_base()  # pylint: disable=invalid-name

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number1 = Column(Integer, default=1, nullable=False, info=dict(const=1))
        number2 = Column(Integer, default=1, nullable=True, info=dict(const=1))
        number3 = Column(Integer, default=lambda: 1, nullable=False)
        number4 = Column(Integer, default=lambda: 1, nullable=True)
        number5 = Column(Integer, default=None, nullable=False)
        number6 = Column(Integer, default=None, nullable=True)
        number7 = Column(Integer, default=1, nullable=False)
        number8 = Column(Integer, default=1, nullable=True)

    # Act
    TestPydantic = model_from(Test, transform=nonify)  # pylint: disable=invalid-name
    test = TestPydantic()

    # Assert
    assert getattr(test, "id", 2) is None
    assert getattr(test, "number1", 2) is None
    assert getattr(test, "number2", 2) is None
    assert getattr(test, "number3", 2) is None
    assert getattr(test, "number4", 2) is None
    assert getattr(test, "number5", 2) is None
    assert getattr(test, "number6", 2) is None
    assert getattr(test, "number7", 2) is None
    assert getattr(test, "number8", 2) is None

    assert TestPydantic.schema() == {
        "title": "Test",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "number1": {"title": "Number1", "type": "integer"},
            "number2": {"title": "Number2", "type": "integer"},
            "number3": {"title": "Number3", "type": "integer"},
            "number4": {"title": "Number4", "type": "integer"},
            "number5": {"title": "Number5", "type": "integer"},
            "number6": {"title": "Number6", "type": "integer"},
            "number7": {"title": "Number7", "type": "integer"},
            "number8": {"title": "Number8", "type": "integer"},
        },
    }
