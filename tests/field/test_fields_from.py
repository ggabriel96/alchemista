import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

from alchemista.field import fields_from


def test_exclude() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number1 = Column(Integer)
        number2 = Column(Integer)
        number3 = Column(Integer)

    # Act
    fields = fields_from(Test, exclude={"id", "number2"})

    # Assert
    assert len(fields) == 2
    assert "number1" in fields
    assert "number3" in fields


def test_include() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number1 = Column(Integer)
        number2 = Column(Integer)
        number3 = Column(Integer)

    # Act
    fields = fields_from(Test, include={"id", "number2"})

    # Assert
    assert len(fields) == 2
    assert "id" in fields
    assert "number2" in fields


def test_exclude_and_include_are_mutually_exclusive() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number1 = Column(Integer)
        number2 = Column(Integer)
        number3 = Column(Integer)

    # Act / Assert
    with pytest.raises(ValueError) as ex:
        fields_from(Test, exclude={"number1"}, include={"id", "number2"})
    assert str(ex.value) == "`exclude` and `include` are mutually-exclusive"
