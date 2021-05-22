# pylint: disable=invalid-name
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

from alchemista import sqlalchemy_to_pydantic


def test_model_names_come_from_dunder_name() -> None:
    # Arrange
    Base = declarative_base()

    class ModelA(Base):
        __tablename__ = "a"
        id = Column(Integer, primary_key=True)

    class ModelB(Base):
        __tablename__ = "b"
        id = Column(Integer, primary_key=True)

    # Act
    ModelAPydantic = sqlalchemy_to_pydantic(ModelA)
    ModelBPydantic = sqlalchemy_to_pydantic(ModelB)

    # Assert
    assert ModelAPydantic.__name__ == "ModelA"
    assert ModelAPydantic.schema() == {
        "title": "ModelA",
        "type": "object",
        "properties": {"id": {"title": "Id", "type": "integer"}},
        "required": ["id"],
    }

    assert ModelBPydantic.__name__ == "ModelB"
    assert ModelBPydantic.schema() == {
        "title": "ModelB",
        "type": "object",
        "properties": {"id": {"title": "Id", "type": "integer"}},
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
