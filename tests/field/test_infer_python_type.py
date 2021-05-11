import datetime as dt
import enum
from typing import List

import pytest
from sqlalchemy import ARRAY, Column, Enum, Integer, Interval
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy_utc import UtcDateTime

from pydantic_sqlalchemy.field import infer_python_type


def test_direct_python_type_is_preferred_to_impl() -> None:
    # Arrange
    column = Column("col", Interval)

    # Act
    python_type = infer_python_type(column)

    # Assert
    assert python_type is dt.timedelta


def test_fallback_to_python_type_from_impl() -> None:
    # Arrange
    column = Column("col", UtcDateTime)

    # Act
    python_type = infer_python_type(column)

    # Assert
    assert python_type is dt.datetime


def test_enum() -> None:
    # Arrange
    class Bool(str, enum.Enum):
        FALSE = "F"
        TRUE = "T"

    boolean = Column("bool", Enum(Bool))

    # Act
    python_type = infer_python_type(boolean)

    # Assert
    assert python_type is Bool


def test_array() -> None:
    # Arrange
    array = Column("array", ARRAY(item_type=Integer))

    # Act
    python_type = infer_python_type(array)

    # Assert
    assert python_type is List[int]


def test_raises_exception_when_type_cannot_be_inferred() -> None:
    # Arrange
    column = Column("col", HSTORE)

    # Act / Assert
    with pytest.raises(RuntimeError) as ex:
        infer_python_type(column)
    assert str(ex.value) == (
        "Could not infer the Python type for col. Check if the column type has a `python_type` in it or in `impl`"
    )
