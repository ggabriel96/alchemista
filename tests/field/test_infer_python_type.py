import datetime as dt
import enum
from decimal import Decimal
from typing import List, Optional

import pytest
from sqlalchemy import Column, Integer, types
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy_utc import UtcDateTime

from alchemista.field import infer_python_type


def test_fallback_to_python_type_from_impl() -> None:
    # Arrange
    column = Column("column", UtcDateTime, nullable=False)

    # Act
    inferred_type = infer_python_type(column)

    # Assert
    assert inferred_type is dt.datetime


def test_nullable_scalar_becomes_optional_scalar() -> None:
    # Arrange
    column = Column("column", Integer, nullable=True)

    # Act
    inferred_type = infer_python_type(column)

    # Assert
    assert inferred_type is Optional[int]


def test_nullable_array_becomes_optional_list() -> None:
    # Arrange
    column = Column("column", types.ARRAY(Integer), nullable=True)

    # Act
    inferred_type = infer_python_type(column)

    # Assert
    assert inferred_type is Optional[List[int]]


def test_enum() -> None:
    # Arrange
    class Bool(str, enum.Enum):
        FALSE = "F"
        TRUE = "T"

    boolean = Column("bool", types.Enum(Bool), nullable=False)

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
    ],
)
def test_common_types(sa_type: types.TypeEngine, expected_type: type) -> None:  # type: ignore[type-arg]
    # Arrange
    column = Column("column", sa_type, nullable=False)

    # Act
    inferred_type = infer_python_type(column)

    # Assert
    assert inferred_type is expected_type


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
    ],
)
def test_array(sa_type: types.TypeEngine, expected_type: type) -> None:  # type: ignore[type-arg]
    # Arrange
    array = Column("array", types.ARRAY(item_type=sa_type), nullable=False)

    # Act
    inferred_type = infer_python_type(array)

    # Assert
    assert inferred_type is List[expected_type]  # type: ignore[valid-type]


def test_enum_array() -> None:
    # Arrange
    class Bool(str, enum.Enum):
        FALSE = "F"
        TRUE = "T"

    array = Column("array", types.ARRAY(item_type=types.Enum(Bool)), nullable=False)

    # Act
    inferred_type = infer_python_type(array)

    # Assert
    assert inferred_type is List[Bool]


def test_raises_exception_when_type_cannot_be_inferred() -> None:
    # Arrange
    column = Column("column", HSTORE)

    # Act / Assert
    with pytest.raises(RuntimeError) as ex:
        infer_python_type(column)
    assert str(ex.value) == (
        "Could not infer the Python type for column. Check if the column type has a `python_type` in it or in `impl`"
    )
