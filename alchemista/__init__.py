try:  # pragma: nocover
    from importlib.metadata import version  # type: ignore
except ImportError:
    from importlib_metadata import version

from alchemista.main import sqlalchemy_to_pydantic

__version__ = version(__package__)
__all__ = ["sqlalchemy_to_pydantic"]
