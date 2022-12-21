import logging
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field


class Schema(BaseSettings):
    """Defines the schema and default values for application settings"""

    # Settings for the database connection
    user: str = Field(title='Database Username', default='egon_user', description='Username for the database')
    password: str = Field(title='Database Password', default='egon_password', description='Password for the database')
    host: str = Field(title='Database Host', default='127.0.0.1', description='Address for the running database host')
    port: int = Field(title='Database Port', default=5432, description='Port number for accessing the database host')
    database: str = Field(title='Database Name', default='egon', description='Application database name')


class ApplicationSettings:
    """Configurable application settings object

    Use the ``configure`` method to override individual default settings.
    Use the ``configure_from_file`` method to load settings from a settings file.
    """

    _cached_settings: Schema = Schema()

    @classmethod
    def load_from_file(cls, path: Path) -> None:
        """Reset application settings to default values

        Values defined in the given file path are used to override defaults.

        Args:
            path: Path to load settings from
        """

        logging.debug(f'Looking for settings file: {path.resolve()}')

        try:
            cls._cached_settings = Schema.parse_file(path)

        except Exception:
            logging.error('settings file is invalid')
            raise

        logging.info(f'Loaded settings from file: {path.resolve()}')

    @classmethod
    def set(cls, **kwargs) -> None:
        """Update values in the application settings

        Unlike the ``configure`` and ``configure_from_file`` methods,
        application settings not specified as keyword arguments are left
        unchanged.

        Raises:
            ValueError: If the item name is not a valid setting
        """

        for item, value in kwargs.items():
            if not hasattr(cls._cached_settings, item):
                ValueError(f'Invalid settings option: {item}')

            setattr(cls._cached_settings, item, value)

    @classmethod
    def get(cls, item: str) -> Any:
        """Return a value from application settings

        Args:
            item: Name of the settings value to retrieve

        Returns
           The value currently configured in application settings
        """

        return getattr(cls._cached_settings, item)
