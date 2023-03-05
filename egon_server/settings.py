"""Parses application settings from external configuration sources.

Order of priority when resolving application settings:
  1. Environment variables prefixed by the string ``EGON_``
  2. Values loaded from a dotenv (.env) file
  3. Values loaded from the secrets' directory ``/etc/egon_server/secrets``
  4. Default values defined by the ``Settings`` class
"""

from pathlib import Path

from pydantic import BaseSettings, Field

_SECRETS_DIR = Path('/etc/egon_server/secrets')


class Settings(BaseSettings):
    """Defines the application settings schema"""

    # Settings for the database connection
    db_user: str = Field(title='Database Username', default='egon_user', description='Database username')
    db_password: str = Field(title='Database Password', default='egon_password', description='Database password')
    db_host: str = Field(title='Database Host', default='127.0.0.1', description='Database host address')
    db_port: int = Field(title='Database Port', default=5432, description='Port number for accessing the database host')
    db_name: str = Field(title='Database Name', default='egon', description='Application database name')

    def get_db_uri(self) -> str:
        """Return the fully qualified database URI"""

        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    class Config:
        """Configure settings parsing options"""

        allow_mutation = False
        env_prefix = "EGON_"
        case_sensitive = False

        # Only look for secrets if the exits - avoids pydantic warnings/errors
        if _SECRETS_DIR.exists():
            secrets_dir = _SECRETS_DIR
