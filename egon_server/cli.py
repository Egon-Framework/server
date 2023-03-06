"""The application command line interface."""

from argparse import ArgumentParser
from pathlib import Path

import uvicorn
from alembic import config, command

from . import __version__
from .api import AppFactory
from .orm import __db_version__, DBConnection
from .settings import Settings

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5000
MIGRATIONS_DIR = Path(__file__).parent / 'migrations'


class Parser(ArgumentParser):
    """Defines the command line interface and handles command line argument parsing"""

    def __init__(self) -> None:
        """Define the command line interface"""

        super().__init__(prog='egon-server', description='Administrative utility for the Egon API server.')
        self.add_argument('--version', action='version', version=__version__)
        subparsers = self.add_subparsers(parser_class=ArgumentParser, required=True)

        migrate = subparsers.add_parser('migrate', description='Migrate the database schema to the latest version.')
        migrate.set_defaults(action=Application.migrate_db)

        serve = subparsers.add_parser('serve', description='Launch a new API server instance.')
        serve.set_defaults(action=Application.serve_api)
        serve.add_argument('--host', type=str, default=DEFAULT_HOST, help='the hostname to listen on')
        serve.add_argument('--port', type=int, default=DEFAULT_PORT, help='the port of the webserver')


class Application:
    """Entry point for instantiating and executing the application"""

    settings = Settings()

    @classmethod
    def migrate_db(cls, schema_version: str = __db_version__) -> None:
        """Migrate the application database to the current schema

        Args:
            schema_version: The schema version to migrate to
        """

        alembic_cfg = config.Config()
        alembic_cfg.set_main_option('script_location', str(MIGRATIONS_DIR))
        alembic_cfg.set_main_option('sqlalchemy.url', cls.settings.get_db_uri())

        # Upgrade/downgrade commands are null if the destination version is
        # below/above the current revision
        command.upgrade(alembic_cfg, schema_version)
        command.downgrade(alembic_cfg, schema_version)

    @classmethod
    def serve_api(cls, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        """Launch the API web server on the given host and port

        Args:
            host: the hostname to listen on
            port: the port of the webserver
        """

        app = AppFactory()
        DBConnection.configure(url=cls.settings.get_db_uri())
        uvicorn.run(app, host=host, port=port)

    @classmethod
    def execute(cls) -> None:
        """Parse command line arguments and run the application"""

        parser = Parser()
        args = vars(parser.parse_args())
        action = args.pop('action')
        action(**args)
