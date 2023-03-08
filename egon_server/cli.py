"""The application command line interface."""

from argparse import ArgumentParser
from pathlib import Path

import uvicorn
from alembic import config, command

from . import __version__
from .api import AppFactory
from .orm import __db_version__, DBConnection
from .settings import Settings

SETTINGS = Settings()
DEFAULT_HOST = SETTINGS.server_host
DEFAULT_PORT = SETTINGS.server_port
DEFAULT_WORKERS = SETTINGS.server_port
DEFAULT_PROXY = SETTINGS.server_port
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
        serve.add_argument('--workers', type=int, default=DEFAULT_WORKERS, help='number of worker processes to spawn')
        serve.add_argument('--proxy', action='store_true', default=DEFAULT_PROXY, help='configure the server to run behind a proxy')


class Application:
    """Entry point for instantiating and executing the application"""

    app = AppFactory()

    @classmethod
    def migrate_db(cls, schema_version: str = __db_version__) -> None:
        """Migrate the application database to the current schema

        Args:
            schema_version: The schema version to migrate to
        """

        alembic_cfg = config.Config()
        alembic_cfg.set_main_option('script_location', str(MIGRATIONS_DIR))
        alembic_cfg.set_main_option('sqlalchemy.url', SETTINGS.get_db_uri())

        # Upgrade/downgrade commands are null operations if the destination
        # version is below/above the current revision
        command.upgrade(alembic_cfg, schema_version)
        command.downgrade(alembic_cfg, schema_version)

    @classmethod
    def serve_api(
        cls,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        workers: int = DEFAULT_WORKERS,
        proxy: bool = DEFAULT_PROXY
    ) -> None:
        """Launch the API web server on the given host and port

        Args:
            host: the hostname to listen on
            port: the port of the webserver
            workers: Number of worker processes to spawn
            proxy: Configure the server to run behind a proxy
        """

        DBConnection.configure(url=SETTINGS.get_db_uri())
        uvicorn.run(
            app='egon_server.cli:Application.app',
            host=host,
            port=port,
            workers=workers,
            proxy_headers=proxy,
            log_config=SETTINGS.get_logging_config())

    @classmethod
    def execute(cls) -> None:
        """Parse command line arguments and run the application"""

        parser = Parser()
        args = vars(parser.parse_args())
        action = args.pop('action')
        action(**args)
