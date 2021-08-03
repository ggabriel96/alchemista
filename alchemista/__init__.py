from importlib.metadata import version

from alchemista.field import fields_from_deprecated as fields_from
from alchemista.model import model_from

__version__ = version(__package__)
__all__ = ["fields_from", "model_from"]
