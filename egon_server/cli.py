"""The application command line interface."""

from argparse import ArgumentParser
from pathlib import Path

import waitress
from flask import Flask
from flask_alembic import Alembic

from . import __version__
from .api import AppFactory
from .orm import __db_version__, db
from .settings import Settings

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5000
MIGRATIONS_DIR = Path(__file__).parent / 'migrations'


class Parser(ArgumentParser):
    """Application commandline parser

    Defines the application command line interface and handles parsing of
    command line arguments.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Define the command line interface"""

        super().__init__(*args, **kwargs)
        self.add_argument('--version', action='version', version=__version__)
        self.subparsers = self.add_subparsers(parser_class=ArgumentParser, required=True)

        migrate = self.subparsers.add_parser('migrate')
        migrate.set_defaults(action=Application.migrate_db)

        serve = self.subparsers.add_parser('serve')
        serve.set_defaults(action=Application.serve_api)
        serve.add_argument('--host', type=str, default=DEFAULT_HOST, help='the hostname to listen on')
        serve.add_argument('--port', type=int, default=DEFAULT_PORT, help='the port of the webserver')


class Application:
    """Entry point for instantiating and executing the application"""

    @staticmethod
    def __initialize_db(app: Flask) -> None:
        """Initialize database connection settings for a flask application"""

        s = Settings()
        uri = f'postgresql://{s.db_user}:{s.db_password}@{s.db_host}:{s.db_port}/{s.db_name}'
        app.config['SQLALCHEMY_DATABASE_URI'] = uri
        db.init_app(app)

    @staticmethod
    def __initialize_alembic(app: Flask) -> None:
        """Initialize alembic functionality for a flask application"""

        # Make sure alembic identifies migration scripts in the correct location
        Alembic(app).init_app(app)
        app.config['ALEMBIC']['script_location'] = str(MIGRATIONS_DIR)

    @classmethod
    def _initialize_app(cls, app: Flask) -> None:
        """Initialize a new flask application

        Args:
            app: The flask application to initialize
        """

        cls.__initialize_db(app)
        cls.__initialize_alembic(app)

    @classmethod
    def migrate_db(cls, schema_version: str = __db_version__) -> None:
        """Migrate the application database to the current schema

        Args:
            schema_version: The schema version to migrate to
        """

        flask_app = AppFactory()
        cls._initialize_app(flask_app)
        with flask_app.app_context():
            Alembic(flask_app).upgrade(target=schema_version)

    @classmethod
    def serve_api(cls, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        """Run the application

        Args:
            host: the hostname to listen on
            port: the port of the webserver
        """

        flask_app = AppFactory()
        cls._initialize_app(flask_app)
        waitress.serve(flask_app, host=host, port=port)

    @classmethod
    def execute(cls) -> None:
        """Parse arguments and run the application"""

        parser = Parser(
            prog='egon-server',
            description='Administrative utility for the Egon backend server')

        args = vars(parser.parse_args())
        action = args.pop('action')
        action(**args)
