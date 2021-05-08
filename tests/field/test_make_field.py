from sqlalchemy import Column, String

from pydantic_sqlalchemy.field import make_field


def test_default_comes_from_column_definition() -> None:
    # Arrange
    column = Column("col", String, default="default")

    # Act
    field = make_field(column)

    # Assert
    assert field.default == "default"
