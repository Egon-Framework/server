"""Parses application settings from external configuration sources.

Order of priority when resolving application settings:
  1. Environment variables prefixed by the string ``EGON_``
  2. Values loaded from a dotenv (.env) file
  3. Values loaded from the secrets' directory ``/etc/egon_server/secrets``
  4. Default values defined by the ``Settings`` class
"""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Literal

from pydantic import BaseSettings, Field

_SECRETS_DIR = Path('/etc/egon_server/secrets')


class Settings(BaseSettings):
    """Defines the application settings schema"""

    class Config:
        """Configure settings parsing options"""

        # Only look for secrets if the directory exits - avoids pydantic warnings/errors
        if _SECRETS_DIR.exists():
            secrets_dir = _SECRETS_DIR

        env_prefix = "EGON_"
        case_sensitive = True
        allow_mutation = False

    # Settings for the database connection
    db_user: str = Field(title='Database Username', default='egon_user', description='Database username')
    db_password: str = Field(title='Database Password', default='egon_password', description='Database password')
    db_host: str = Field(title='Database Host', default='127.0.0.1', description='Database host address')
    db_port: int = Field(title='Database Port', default=5432, description='Database port number')
    db_name: str = Field(title='Database Name', default='egon', description='Application database name')

    # Settings for application logs
    log_path: Optional[Path] = Field(title='Log Path', default=None, description='Log file path')
    log_max_size: int = Field(title='Log Max Size', default=10000, description='Maximum log file size before rotating')
    log_rotations: int = Field(title='Log rotations', default=5, description='Total log file rotations to keep')
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        title='Logging Level', default='INFO', description='Logging threshold for recording to the log file')

    def get_db_uri(self) -> str:
        """Return the fully qualified database URI"""

        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    def get_logging_config(self) -> dict:
        """Return a dictionary with configuration settings for the Python logger"""

        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'default': {
                    'format': '%(asctime)s [%(process)d] %(levelname)8s %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'default',
                    'level': 0
                },
                'log_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'default',
                    'level': self.log_level,
                    'filename': self.log_path or NamedTemporaryFile().name,
                    'maxBytes': self.log_max_size,
                    'backupCount': self.log_rotations,
                    'delay': 'True'
                }
            },
            'loggers': {
                'uvicorn': {'handlers': ['console', 'log_file'], 'level': 'INFO', 'propagate': False},
                'uvicorn.error': {'handlers': ['console', 'log_file'], 'level': 'INFO', 'propagate': False},
                'uvicorn.access': {'handlers': ['console', 'log_file'], 'level': 'INFO', 'propagate': False},
                'root': {'handlers': ['console', 'log_file'], 'level': 'INFO', 'propagate': False}
            }
        }
