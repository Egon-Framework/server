"""Parses application settings from external configuration sources.

Order of priority when resolving application settings:
  1. Environment variables prefixed by the string ``EGON_``
  2. Values loaded from a dotenv (.env) file
  3. Values loaded from the secrets' directory ``/etc/egon_server/secrets``
  4. Default values defined by the ``Settings`` class
"""

from pathlib import Path
from typing import Optional, Literal

from pydantic import BaseSettings, Field

_SECRETS_DIR = Path('/etc/egon_server/secrets')


# TODO:
# - Add user identifier to access logs
# - Add configuration for alembic logger
# - Consider using multiple log files for db, server, access
# - Add different formats for different destinations (color coding?)

class Settings(BaseSettings):
    """Defines the application settings schema"""

    class Config:
        """Configure settings parsing options"""

        # Only look for secrets if the directory exits - avoids pydantic warnings/errors
        if _SECRETS_DIR.exists():
            secrets_dir = _SECRETS_DIR

        allow_mutation = False
        env_prefix = "EGON_"
        case_sensitive = False

    # Settings for the database connection
    db_user: str = Field(title='Database Username', default='egon_user', description='Database username')
    db_password: str = Field(title='Database Password', default='egon_password', description='Database password')
    db_host: str = Field(title='Database Host', default='127.0.0.1', description='Database host address')
    db_port: int = Field(title='Database Port', default=5432, description='Database port number')
    db_name: str = Field(title='Database Name', default='egon', description='Application database name')

    # Settings for the smtp server
    smtp_user: Optional[str] = Field(title='SMTP Username', default=None, description='SMTP username')
    smtp_password: Optional[str] = Field(title='SMTP Password', default=None, description='SMTP password')
    smtp_host: str = Field(title='SMTP Host', default='localhost', description='SMTP server hostname')
    smtp_port: int = Field(title='SMTP port', default=587, description='SMTP server port number')

    # Settings for admin notifications
    admin_emails: list[str] = Field(title='Admin emails', default=[], description='Admin notification emails')
    admin_threshold: Literal['WARNING', 'ERROR', 'CRITICAL'] = Field(
        title='Admin notification threshold', default='ERROR', description='Admin notification level.')

    # Settings for application logs
    log_path: Optional[Path] = Field(title='Log Path', default=None, description='Log file path')
    log_max_size: int = Field(title='Log Max Size', default=10000, description='Maximum log file size before rotating')
    log_rotations: int = Field(title='Log rotations', default=5, description='Total log file rotations to keep')
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        title='Logging Level', default='INFO', description='Application logging level')

    def get_db_uri(self) -> str:
        """Return the fully qualified database URI"""

        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    def get_log_settings(self) -> dict:
        """Return a dictionary with configuration settings for the Python logger"""

        logging_config = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)8s %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 0,
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout',
                },
            },
            'loggers': {
                'uvicorn': {
                    'handlers': ['console'],
                    'level': 0,
                    'propagate': False
                },
                'uvicorn.error': {
                    'level': 0,
                    'handlers': ['console'],
                    'propagate': False
                },
                'uvicorn.access': {
                    'handlers': ['console'],
                    'level': 0,
                    'propagate': False
                }
            },
            'root': {
                'handlers': ['console'],
                'level': 0,
            }
        }

        if self.log_path is not None:
            logging_config['handlers']['log_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': self.log_level,
                'formatter': 'default',
                'filename': '/var/log/egon_api_server.log',
                'maxBytes': 10000,
                'backupCount': 10,
                'delay': 'True'}

            logging_config['root']['handlers'].append('log_file')
            for logger in logging_config['loggers'].values():
                logger['handlers'].append('log_file')

        if self.admin_emails:
            logging_config['handlers']['admin_email'] = {
                'class': 'logging.handlers.SMTPHandler',
                'level': self.admin_threshold,
                'formatter': 'default',
                'mailhost': (self.smtp_host, self.smtp_port),
                'fromaddr': 'donotreply@egonframework.com',
                'toaddrs': self.admin_emails,
                'subject': f'Egon API Server Notification',
                'credentials': (self.smtp_user, self.smtp_password) if self.smtp_user else None}

            logging_config['root']['handlers'].append('admin_email')
            for logger in logging_config['loggers'].values():
                logger['handlers'].append('admin_email')

        return logging_config
