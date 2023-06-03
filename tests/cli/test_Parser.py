"""Tests for the ``cli.Parser`` class."""

from unittest import TestCase

from egon_server.cli import Parser, Application
from egon_server.settings import Settings


class DefaultParser(TestCase):
    """Test the root CLI parser"""

    def test_program_name(self) -> None:
        """Test the CLI application name is set to ``egon-server``"""

        self.assertEqual('egon-server', Parser().prog)

    def test_default_action(self) -> None:
        """Test the default callable action when parsing no arguments is ``None``"""

        self.assertIsNone(Parser().parse_args([]).action)


class MigrateSubparser(TestCase):
    """Test the ``migrate`` subparser"""

    def test_action_matches_application(self) -> None:
        """Test the subparser is configured to call the correct ``Application`` method"""

        self.assertEqual(Application.migrate_db, Parser().parse_args(['migrate']).action)


class ServeSubparser(TestCase):
    """Test the ``serve`` command"""

    def test_defaults_match_settings(self) -> None:
        """Test CLI defaults match the values defined in application settings"""

        args = Parser().parse_args(['serve'])

        settings = Settings()
        self.assertEqual(settings.server_host, args.host)
        self.assertEqual(settings.server_port, args.port)
        self.assertEqual(settings.server_workers, args.workers)

    def test_values_overwritten(self) -> None:
        """Test custom values overwrite default values"""

        args = Parser().parse_args(['serve', '--host', 'my.example.com', '--port', '100', '--workers', '99'])

        # The following checks also implicitly test argument type casting
        self.assertEqual('my.example.com', args.host)
        self.assertEqual(100, args.port)
        self.assertEqual(99, args.workers)

    def test_action_matches_application(self) -> None:
        """Test the subparser is configured to call the correct ``Application`` method"""

        self.assertEqual(Application.serve_api, Parser().parse_args(['serve']).action)


class ErrorHandling(TestCase):
    """Test error handling via the ``error`` method"""

    def test_raised_as_system_exit(self) -> None:
        """Test the ``error`` method raises a ``SystemExit`` error"""

        with self.assertRaises(SystemExit):
            Parser().error('This is an error')

    def test_raised_with_message(self) -> None:
        """Test the exit message is included with raised error"""

        message = 'This is a test'
        with self.assertRaisesRegex(SystemExit, message):
            Parser().error(message)
