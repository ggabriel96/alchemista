import datetime as dt
import time
from typing import Any, Dict

import pytest
from pydantic.fields import Undefined
from sqlalchemy import Column, Integer, String, Text

from alchemista.field import FieldKwargs, make_field


def test_field_kwargs_used_as_info() -> None:
    # Arrange
    column = Column(
        Integer,
        info=FieldKwargs(
            alias="n",
            const=0,
            description="Some multiple of 2",
            ge=0,
            le=100,
            multiple_of=2,
            title="Multiple of Two",
        ),
    )

    # Act
    field = make_field(column)

    # Assert
    assert field.alias == "n"
    assert field.alias_priority == 2
    assert field.const == 0
    assert field.default is None
    assert field.default_factory is None
    assert field.description == "Some multiple of 2"
    assert field.extra == {}
    assert field.ge == 0
    assert field.gt is None
    assert field.le == 100
    assert field.lt is None
    assert field.max_items is None
    assert field.max_length is None
    assert field.min_items is None
    assert field.min_length is None
    assert field.multiple_of == 2
    assert field.regex is None
    assert field.title == "Multiple of Two"


def test_default_comes_from_column_definition() -> None:
    # Arrange
    column = Column(Integer, default=2)

    # Act
    field = make_field(column)

    # Assert
    assert field.default == 2

    assert field.alias is None
    assert field.alias_priority is None
    assert field.const is None
    assert field.default_factory is None
    assert field.description is None
    assert field.extra == {}
    assert field.ge is None
    assert field.gt is None
    assert field.le is None
    assert field.lt is None
    assert field.max_items is None
    assert field.max_length is None
    assert field.min_items is None
    assert field.min_length is None
    assert field.multiple_of is None
    assert field.regex is None
    assert field.title is None


@pytest.mark.parametrize(
    "doc,info,expected",
    [
        ("Description from doc attribute", None, "Description from doc attribute"),
        ("Description from doc attribute", dict(description=None), None),
        (
            "Description from doc attribute",
            dict(description="Description from info is preferred"),
            "Description from info is preferred",
        ),
    ],
)
def test_description(doc: str, info: Dict[str, Any], expected: str) -> None:
    # Arrange
    column = Column(Text, doc=doc, info=info)

    # Act
    field = make_field(column)

    # Assert
    assert field.description == expected

    assert field.alias is None
    assert field.alias_priority is None
    assert field.const is None
    assert field.default is None
    assert field.default_factory is None
    assert field.extra == {}
    assert field.ge is None
    assert field.gt is None
    assert field.le is None
    assert field.lt is None
    assert field.max_items is None
    assert field.max_length is None
    assert field.min_items is None
    assert field.min_length is None
    assert field.multiple_of is None
    assert field.regex is None
    assert field.title is None


def test_length_comes_from_column_definition() -> None:
    # Arrange
    column = Column(String(64))

    # Act
    field = make_field(column)

    # Assert
    assert field.max_length == 64

    assert field.alias is None
    assert field.alias_priority is None
    assert field.const is None
    assert field.default is None
    assert field.default_factory is None
    assert field.description is None
    assert field.extra == {}
    assert field.ge is None
    assert field.gt is None
    assert field.le is None
    assert field.lt is None
    assert field.max_items is None
    assert field.min_items is None
    assert field.min_length is None
    assert field.multiple_of is None
    assert field.regex is None
    assert field.title is None


def test_length_from_info_must_match_column_definition() -> None:
    # Arrange
    max_length = 64
    column = Column("column", String(max_length), info=dict(max_length=max_length + 1))

    # Act / Assert
    with pytest.raises(ValueError) as ex:
        make_field(column)
    assert str(ex.value) == (
        f"max_length ({max_length + 1}) of `info` differs from length set in column type ({max_length}) on column"
        f" `{column.name}`. Either remove max_length from `info` (preferred) or set them to equal values"
    )


def test_lambda_as_default_factory() -> None:
    # Arrange
    default_factory = lambda: "dynamic default"
    column = Column(Text, default=default_factory)

    # Act
    field = make_field(column)

    # Assert
    assert field.default is Undefined
    assert field.default_factory is default_factory
    assert field.default_factory() == "dynamic default"

    assert field.alias is None
    assert field.alias_priority is None
    assert field.const is None
    assert field.description is None
    assert field.extra == {}
    assert field.ge is None
    assert field.gt is None
    assert field.le is None
    assert field.lt is None
    assert field.max_items is None
    assert field.max_length is None
    assert field.min_items is None
    assert field.min_length is None
    assert field.multiple_of is None
    assert field.regex is None
    assert field.title is None


def test_datetime_now_as_default_factory() -> None:
    # Arrange
    default_factory = dt.datetime.now
    column = Column(Text, default=default_factory)

    # Act
    field = make_field(column)

    # Assert
    assert field.default is Undefined
    assert field.default_factory is default_factory

    now1 = field.default_factory()
    time.sleep(0.1)
    now2 = field.default_factory()
    assert isinstance(now1, dt.datetime)
    assert isinstance(now2, dt.datetime)
    assert now1 < now2

    assert field.alias is None
    assert field.alias_priority is None
    assert field.const is None
    assert field.description is None
    assert field.extra == {}
    assert field.ge is None
    assert field.gt is None
    assert field.le is None
    assert field.lt is None
    assert field.max_items is None
    assert field.max_length is None
    assert field.min_items is None
    assert field.min_length is None
    assert field.multiple_of is None
    assert field.regex is None
    assert field.title is None
