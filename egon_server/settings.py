"""The application settings schema is defined by the ``Settings`` class.
Settings are loaded at runtime and cached under the ``SETTINGS`` variable
according to the following priority order:
  1. Commandline arguments provided at runtime (see the ``cli`` module)
  2. Environment variables prefixed by the string ``EGON_``
  3. Values loaded from the secrets' directory ``/etc/egon_server/secrets``
  4. Default values defined by the ``Settings`` class
"""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Defines the application settings schema"""

    class Config:
        """Configure settings parsing options"""

        # Only look for secrets if the directory exists - avoids pydantic warnings/errors
        _secrets_dir = Path('/etc/egon_server/secrets')
        if _secrets_dir.exists():
            secrets_dir = _secrets_dir

        env_prefix = "EGON_"
        case_sensitive = False
        allow_mutation = False

    # Settings for the Uvicorn ASGI server
    server_host: str = Field(title='API Server Host', default='localhost', description='API server host address')
    server_port: int = Field(title='API Server Port', default=5000, description='API server port number')
    server_workers: int = Field(title='Web server workers', default=1, description='Server processes to spawn')

    # Settings for the database connection
    db_user: str = Field(title='Database Username', default='egon_user', description='Database username')
    db_password: str = Field(title='Database Password', default='egon_password', description='Database password')
    db_host: str = Field(title='Database Host', default='localhost', description='Database host address')
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
                # Loggers for the Uvicorn ASGI server
                'uvicorn': {'handlers': ['console', 'log_file'], 'level': 'INFO', 'propagate': False},
                'uvicorn.error': {'handlers': ['console', 'log_file'], 'level': 'INFO', 'propagate': False},
                'uvicorn.access': {'handlers': ['console', 'log_file'], 'level': 'INFO', 'propagate': False},

                # Custom loggers allowing the application logs to specific destinations
                'console_logger': {'handlers': ['console'], 'level': 0, 'propagate': False},
                'file_logger': {'handlers': ['log_file'], 'level': 0, 'propagate': False},

                # The root logger - configured so logs are written to all destinations
                '': {'handlers': ['console', 'log_file'], 'level': 0, 'propagate': False}
            }
        }


# Load settings from disk/environment
SETTINGS = Settings()
