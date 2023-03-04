import importlib.metadata
from logging.config import dictConfig

from . import settings

__version__ = importlib.metadata.version(__package__)

# Configure application logging
dictConfig(settings.Settings().get_log_settings())
