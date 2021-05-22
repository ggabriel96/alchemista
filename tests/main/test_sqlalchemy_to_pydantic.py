# pylint: disable=invalid-name
import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

from alchemista import sqlalchemy_to_pydantic


def test_warns_of_deprecation() -> None:
    # Arrange
    Base = declarative_base()

    class Test(Base):
        __tablename__ = "test"

        id = Column(Integer, primary_key=True)
        number = Column(Integer)

    # Act / Assert
    with pytest.warns(DeprecationWarning):
        sqlalchemy_to_pydantic(Test)
