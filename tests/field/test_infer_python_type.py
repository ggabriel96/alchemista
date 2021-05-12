import datetime as dt
import enum
from decimal import Decimal
from typing import List

import pytest
from sqlalchemy import Column, types
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy_utc import UtcDateTime

from pydantic_sqlalchemy.field import infer_python_type


def test_fallback_to_python_type_from_impl() -> None:
    # Arrange
    column = Column("column", UtcDateTime)

    # Act
    inferred_type = infer_python_type(column)

    # Assert
    assert inferred_type is dt.datetime


def test_enum() -> None:
    # Arrange
    class Bool(str, enum.Enum):
        FALSE = "F"
        TRUE = "T"

    boolean = Column("bool", types.Enum(Bool))

    # Act
    inferred_type = infer_python_type(boolean)

    # Assert
    assert inferred_type is Bool


@pytest.mark.parametrize(
    "sa_type,expected_type",
    [
        (types.BigInteger, int),
        (types.Boolean, bool),
        (types.Date, dt.date),
        (types.DateTime, dt.datetime),
        # (types.Enum, enum.Enum),
        (types.Float, float),
        (types.Integer, int),
        (types.Interval, dt.timedelta),
        (types.LargeBinary, bytes),
        # (types.MatchType, bool),
        (types.Numeric, Decimal),
        (types.PickleType, bytes),
        # (types.SchemaType, None),
        (types.SmallInteger, int),
        (types.String, str),
        (types.Text, str),
        (types.Time, dt.time),
        (types.Unicode, str),
        (types.UnicodeText, str),
        # (types.ARRAY, list),
        (types.BIGINT, int),
        (types.BINARY, bytes),
        (types.BLOB, bytes),
        (types.BOOLEAN, bool),
        (types.CHAR, str),
        (types.CLOB, str),
        (types.DATE, dt.date),
        (types.DATETIME, dt.datetime),
        (types.DECIMAL, Decimal),
        (types.FLOAT, float),
        (types.INT, int),
        (types.INTEGER, int),
        (types.JSON, dict),
        (types.NCHAR, str),
        (types.NUMERIC, Decimal),
        (types.NVARCHAR, str),
        (types.REAL, float),
        (types.SMALLINT, int),
        (types.TEXT, str),
        (types.TIME, dt.time),
        (types.TIMESTAMP, dt.datetime),
        (types.VARBINARY, bytes),
        (types.VARCHAR, str),
    ]
)
def test_common_types(sa_type: types.TypeEngine, expected_type: type) -> None:  # type: ignore[type-arg]
    # Arrange
    column = Column("column", sa_type)

    # Act
    inferred_type = infer_python_type(column)

    # Assert
    assert inferred_type is expected_type


def test_array() -> None:
    # Arrange
    array = Column("array", types.ARRAY(item_type=types.Integer))

    # Act
    inferred_type = infer_python_type(array)

    # Assert
    assert inferred_type is List[int]


def test_raises_exception_when_type_cannot_be_inferred() -> None:
    # Arrange
    column = Column("column", HSTORE)

    # Act / Assert
    with pytest.raises(RuntimeError) as ex:
        infer_python_type(column)
    assert str(ex.value) == (
        "Could not infer the Python type for column. Check if the column type has a `python_type` in it or in `impl`"
    )
