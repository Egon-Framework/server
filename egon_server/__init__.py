import importlib.metadata
import logging.config

from .settings import SETTINGS

try:
    __version__ = importlib.metadata.version(__package__)

except importlib.metadata.PackageNotFoundError:
    __version__ = '0.0.0'

# Configure logging for the application and it's dependencies
logging.config.dictConfig(SETTINGS.get_logging_config())
