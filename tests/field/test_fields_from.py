from pydantic.fields import FieldInfo
from sqlalchemy import Boolean, Column, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

from alchemista.field import fields_from


def test_contains_all_columns_from_model_definition() -> None:
    # Arrange
    Base = declarative_base()  # pylint: disable=invalid-name

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        boolean = Column(Boolean)
        floating_point = Column(Float)
        integer = Column(Integer)
        string = Column(String(64))
        text = Column(Text)

    # Act
    fields = fields_from(Test)

    # Assert
    assert len(fields) == 6
    assert "id" in fields
    assert "boolean" in fields
    assert "floating_point" in fields
    assert "integer" in fields
    assert "string" in fields
    assert "text" in fields
    assert all(isinstance(field, FieldInfo) for field in fields.values())
