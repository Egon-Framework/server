"""The ``cli`` module defines the application's command line interface.
It is responsible for parsing command line arguments and using the resulting
values to configure and launch the parent application.
"""

from argparse import ArgumentParser

from . import __version__


class Parser(ArgumentParser):
    """Application commandline parser

    Defines the application command line interface and handles parsing of
    command line arguments.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Define the command line interface"""

        super().__init__(*args, **kwargs)
        self.add_argument('--version', action='version', version=__version__)


class Application:
    """Entry point for instantiating and executing the application"""

    def __init__(self):
        """Initialize the application"""

        self.parser = Parser(
            prog='egon-server',
            description='Administrative utility for the Egon backend server'
        )

    def execute(self):
        """Parse arguments and run the application"""

        args = self.parser.parse_args()
        print('Hello World')
