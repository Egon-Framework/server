"""Parses application settings from external configuration sources.

Order of priority:

1. Environment variables prefixed by the string ``EGON_``
2. Values loaded from a dotenv (.env) file
3. Values loaded from the secrets' directory ``/etc/egon_server/secrets``
4. Default values defined by the ``Settings`` class
"""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Defines the schema and default values for application settings"""

    # Settings for the database connection
    db_user: str = Field(title='Database Username', default='egon_user', description='Database username')
    db_password: str = Field(title='Database Password', default='egon_password', description='Database password')
    db_host: str = Field(title='Database Host', default='127.0.0.1', description='Database host address')
    db_port: int = Field(title='Database Port', default=5432, description='Port number for accessing the database host')
    db_name: str = Field(title='Database Name', default='egon', description='Application database name')

    class Config:
        """Configure settings parsing options"""

        env_prefix = "EGON_"
        case_sensitive = False
        secrets_dir = '/etc/egon_server/secrets'
