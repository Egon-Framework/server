import importlib.metadata
import logging.config

from .settings import SETTINGS

__version__ = importlib.metadata.version(__package__)

# Configure logging for the application and it's dependencies
logging.config.dictConfig(SETTINGS.get_logging_config())
