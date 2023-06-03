"""Tests for the ``cli.Parser`` class."""

from unittest import TestCase

from egon_server.cli import Parser


class ParserHelpData(TestCase):
    """Test the configuration of parser help data"""

    def test_program_name(self) -> None:
        """Test the CLI application name is set to ``egon-server``"""

        self.assertEqual('egon-server', Parser().prog)


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
