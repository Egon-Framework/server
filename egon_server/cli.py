"""The command line interface is implemented in two parts. The ``Parser`` class
defines the overall interface and handles command line argument parsing. This
includes CLI defaults, help text, and argument type casting. The ``Application``
class encapsulates top level application logic and is  responsible for executing
the instruction set returned by the ``Parser`` class.

The ``Application.execute`` method serves as the default application entrypoint
when executing the parent package from the command line.
"""

import logging
from argparse import ArgumentParser

import uvicorn
from alembic import config, command

from . import __version__
from .api import AppFactory
from .orm import __db_version__, DBConnection, MIGRATIONS_DIR
from .settings import SETTINGS


class Parser(ArgumentParser):
    """Defines the application command line interface and handles command line argument parsing"""

    def __init__(self) -> None:
        """Define the command line interface"""

        super().__init__(prog='egon-server', description='Administrative utility for the Egon API server.')
        self.add_argument('--version', action='version', version=__version__)
        self.set_defaults(callable=None)
        subparsers = self.add_subparsers(parser_class=ArgumentParser, required=False)

        # Subparser for database migrations
        migrate = subparsers.add_parser('migrate', description='Migrate the database schema to the latest version.')
        migrate.set_defaults(callable=Application.migrate_db)

        # Subparser for launching the API server
        serve = subparsers.add_parser('serve', description='Launch a new API server instance.')
        serve.set_defaults(callable=Application.serve_api)
        serve.add_argument('--host', type=str, default=SETTINGS.server_host, help='the hostname to listen on')
        serve.add_argument('--port', type=int, default=SETTINGS.server_port, help='the port to serve on')
        serve.add_argument('--workers', type=int, default=SETTINGS.server_workers, help='number of workers to spawn')

    def error(self, message: str) -> None:
        """Exit the parser by raising a ``SystemExit`` error

        This method mimics the parent class behavior except error messages
        are included in the raised ``SystemExit`` exception. This makes for
        easier testing/debugging.

        Args:
            message: The error message

        Raises:
            SystemExit: Every time the method is run
        """

        raise SystemExit(message)


class Application:
    """Entry point for instantiating and executing API server tasks from the command line"""

    app = AppFactory()

    @classmethod
    def migrate_db(cls, schema_version: str = __db_version__) -> None:
        """Migrate the application database to the given schema version

        Defaults to the schema version expected by the ORM module
        (``orm.__db_version__``).

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
        host: str = SETTINGS.server_host,
        port: int = SETTINGS.server_port,
        workers: int = SETTINGS.server_workers
    ) -> None:
        """Launch the API web server on the given host and port

        Default argument values are set dynamically to reflect the application
        settings file. See the ``settings`` module for more information on
        how settings values are resolved.

        Args:
            host: the hostname to listen on
            port: the port of the webserver
            workers: Number of worker processes to spawn
        """

        DBConnection.configure(url=SETTINGS.get_db_uri())
        uvicorn.run(
            app='egon_server.cli:Application.app',
            host=host,
            port=port,
            workers=workers,
            log_config=SETTINGS.get_logging_config())

    @classmethod
    def execute(cls) -> None:
        """Parse command line arguments and run the application"""

        parser = Parser()
        kwargs = vars(parser.parse_args())

        # If CLI is called without any argument, print the help and exit
        if callable_ := kwargs.pop('callable') is None:
            parser.print_help()
            return

        # Route error messages to application loggers
        try:
            callable_(**kwargs)

        except Exception as excep:
            logging.getLogger('file_logger').critical('Application crash', exc_info=excep)
            logging.getLogger('console_logger').critical(str(excep))
