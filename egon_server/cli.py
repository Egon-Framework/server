"""The application's command line interface."""

from argparse import ArgumentParser

from . import __version__
from .api import flask_app


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

        run = self.subparsers.add_parser('run')
        run.set_defaults(action=Application.run_api)
        run.add_argument('--host', type=str, default='localhost', help='the hostname to listen on')
        run.add_argument('--port', type=int, default=5000, help='the port of the webserver')
        run.add_argument('--debug', action='store_true', default=False, help='enable debug mode (insecure)')


class Application:
    """Entry point for instantiating and executing the application"""

    def __init__(self):
        """Initialize the application"""

        self.parser = Parser(
            prog='egon-server',
            description='Administrative utility for the Egon backend server'
        )

    @staticmethod
    def run_api(host, port, debug: bool = False) -> None:
        """Run the application

        Args:
            host: the hostname to listen on
            port: the port of the webserver
            debug: Enable or disable debug mode
        """

        flask_app.run(host=host, port=port, debug=debug, load_dotenv=False)

    def execute(self) -> None:
        """Parse arguments and run the application"""

        args = vars(self.parser.parse_args())
        action = args.pop('action')
        action(**args)
