# pylint: disable=invalid-name
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

from alchemista import sqlalchemy_to_pydantic


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
