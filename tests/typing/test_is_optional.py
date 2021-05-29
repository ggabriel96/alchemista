from typing import Any, Generic, Optional, TypeVar

import pytest

from alchemista.typing import is_optional


@pytest.mark.parametrize(
    "python_type,expected_result",
    [
        (Any, False),
        (bool, False),
        (bytes, False),
        (bytearray, False),
        (complex, False),
        (dict, False),
        (float, False),
        (frozenset, False),
        (list, False),
        (int, False),
        (memoryview, False),
        (range, False),
        (set, False),
        (str, False),
        (tuple, False),
        (type, False),
        (type(None), False),
        (Optional[Any], True),
        (Optional[bool], True),
        (Optional[bytes], True),
        (Optional[bytearray], True),
        (Optional[complex], True),
        (Optional[dict], True),
        (Optional[float], True),
        (Optional[frozenset], True),
        (Optional[list], True),
        (Optional[int], True),
        (Optional[memoryview], True),
        (Optional[range], True),
        (Optional[set], True),
        (Optional[str], True),
        (Optional[tuple], True),
        (Optional[type], True),
        (Optional[type(None)], False),  # this is weird XD
    ],
)
def test_builtin_types(python_type: type, expected_result: bool) -> None:
    assert is_optional(python_type) is expected_result


def test_type_var() -> None:
    # Arrange
    type_var = TypeVar("type_var")

    # Act / Assert
    assert is_optional(type_var) is False  # type: ignore[arg-type]
    assert is_optional(Optional[type_var]) is True  # type: ignore[arg-type]


def test_generics() -> None:
    # Arrange
    type_var = TypeVar("type_var")

    class Gen(Generic[type_var]):
        pass

    # Act / Assert
    assert is_optional(Gen) is False
    assert is_optional(Optional[Gen]) is True  # type: ignore[arg-type]
