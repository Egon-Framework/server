import logging
from argparse import ArgumentParser
from pathlib import Path

from . import __version__
from .api import flask_app, __api_version__
from .orm import DBConnection
from .settings import ApplicationSettings

SETTINGS_PATH = Path('/etc/egon/server.json')


class Parser(ArgumentParser):
    """Application commandline parser"""

    def __init__(self, *args, **kwargs) -> None:
        """Define arguments for the command line interface"""

        super().__init__(*args, **kwargs)
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('-v', dest='verbose', action='store_true', help='include debug messages in the log')


class Application:
    """Entry point for instantiating and executing the application"""

    @classmethod
    def run(cls, verbose: bool = False) -> None:
        """Run the application

        Args:
            verbose: Include debug messages in the application log file
        """

        cls._configure_logging(verbose=verbose)
        logging.info(f'Launching Egon Server version {__version__} (API {__api_version__})...')

        cls._load_settings()
        cls._setup_database()
        cls._launch_api()

    @classmethod
    def execute(cls) -> None:
        """Parse arguments and run the application"""

        parser = Parser(prog='egon_server')
        args = parser.parse_args()

        try:
            cls.run(verbose=args.verbose)

        except Exception as caught:
            parser.error(str(caught))

    @staticmethod
    def _configure_logging(verbose: bool) -> None:
        """Configure python logging to the given level

        Args:
            verbose: Set the logging level to ``DEBUG`` instead of ``INFO``
        """

        log_format = '%(asctime)s - %(levelname)8s: %(message)s'
        if verbose:
            log_level = logging.DEBUG

        else:
            log_level = logging.INFO

        logging.basicConfig(level=log_level, format=log_format, filename='/var/egon/server.log')

    @staticmethod
    def _load_settings() -> None:
        """Load application settings from disk"""

        logging.info('Checking for custom settings...')
        if SETTINGS_PATH.exists():
            logging.info('Custom settings found.')
            ApplicationSettings.load_from_file(SETTINGS_PATH)

        else:
            logging.info('No custom settings found. Using default values.')
            logging.warning('The default database credentials are not secure and should be customized.')

    @staticmethod
    def _setup_database() -> None:
        """Establish a connection with the application database"""

        logging.info('Connecting to application database...')
        DBConnection.configure(
            user=ApplicationSettings.get('user'),
            password=ApplicationSettings.get('password'),
            host=ApplicationSettings.get('host'),
            port=ApplicationSettings.get('port'),
            database=ApplicationSettings.get('database')
        )

    @staticmethod
    def _launch_api() -> None:
        """Launch the REST API Server"""

        logging.info('Launching API server...')
        flask_app.run()
