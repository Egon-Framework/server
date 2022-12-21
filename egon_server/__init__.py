import importlib.metadata

from api import __api_version__

__version__ = importlib.metadata.version(__package__)
