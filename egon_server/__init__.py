import importlib.metadata
from .orm import __db_version__

__version__ = importlib.metadata.version(__package__)
