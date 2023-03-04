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
    db_port: int = Field(title='Database Port', default=5432, description='Port number for accessing the database host')
    db_name: str = Field(title='Database Name', default='egon', description='Application database name')

    # Settings for admin notifications
    smtp_host: str = Field(title='SMTP Host', default='localhost', description='SMTP server hostname')
    smtp_port: int = Field(title='SMTP port', default=587, description='SMTP server port')
    smtp_user: Optional[str] = Field(title='SMTP Username', default=None, description='SMTP username')
    smtp_password: Optional[str] = Field(title='SMTP Password', default=None, description='SMTP password')

    admin_emails: list[str] = Field(title='Admin emails', default=[], description='Admin notification emails')
    admin_threshold: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        title='Logging Level', default='INFO', description='Application logging level.')

    # Settings for application logs
    log_path: Optional[Path] = Field(title='Log Path', default=None, description='Log file path')
    log_rotations: int = Field(title='Log rotations', default=5, description='Number of log file rotations to keep')
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        title='Logging Level', default='INFO', description='Application logging level.')

    def get_log_settings(self) -> dict:
        """Return a dictionary with configuration settings for the Python logger"""

        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)8s %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'level': 'ERROR',
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout',
                },
                'email': {
                    'class': 'logging.handlers.SMTPHandler',
                    'formatter': 'default',
                    'level': self.admin_threshold,
                    'mailhost': (self.smtp_host, self.smtp_port),
                    'fromaddr': 'donotreply@egonframework.com',
                    'toaddrs': self.admin_emails,
                    'subject': f'Egon API Server Notification',
                    'credentials': (self.smtp_user, self.smtp_password) if self.smtp_user else None,
                },
                'log_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'default',
                    'filename': '/var/log/egon_api_server.log',
                    'maxBytes': 10000,
                    'backupCount': 10,
                    'delay': 'True',
                },
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console', 'log_file', 'email'],
            }
        }
