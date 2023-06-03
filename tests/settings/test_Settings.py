"""Tests for the ``settings.Settings`` class."""

import os
import re
from copy import deepcopy
from unittest import TestCase

from egon_server.settings import Settings


class Config(TestCase):
    """Test the lading/modification of applciation settings"""

    def setUp(self) -> None:
        """Cache current environmental variables"""

        self.old_env = deepcopy(os.environ)

    def tearDown(self) -> None:
        """Restore environmental variables to their pre-test values"""

        os.environ.clear()
        os.environ.update(self.old_env)

    def test_mutation_prohibited(self) -> None:
        """Test settings values are immutable once loaded"""

        with self.assertRaisesRegex(TypeError, '"Settings" is immutable'):
            Settings().server_port = 44

    def test_loads_env_variables(self) -> None:
        """Test settings are loaded from environmental variables"""

        os.environ['EGON_SERVER_PORT'] = '99'
        custom_port = Settings().server_port
        self.assertEqual(99, custom_port)


class GetDbUri(TestCase):
    """Test the ``get_db_uri`` method"""

    def test_values_match_settings(self) -> None:
        """Test URI values match application settings"""

        settings = Settings()
        pattern = re.compile(r'(.*):\/\/(.*):(.*)@(.*):(.*)\/(.*)')
        match = pattern.match(settings.get_db_uri())

        scheme, username, password, host, port, database = match.groups()
        self.assertEqual('postgresql+asyncpg', scheme)
        self.assertEqual(settings.db_user, username)
        self.assertEqual(settings.db_password, password)
        self.assertEqual(settings.db_host, host)
        self.assertEqual(settings.db_port, int(port))
        self.assertEqual(settings.db_name, database)


class GetLoggingConfig(TestCase):
    """Test the ``get_logging_config`` method"""

    def test_uvicorn_loggers(self) -> None:
        """Test the configuration of Uvicorn loggers"""

        config = Settings().get_logging_config()
        for logger_name in ('uvicorn', 'uvicorn.error', 'uvicorn.access'):
            self.assertIn(logger_name, config['loggers'], f'{logger_name} has no configuration')

            # Test handlers are configured for appropriate logging destinations
            handlers = config['loggers'][logger_name]['handlers']
            self.assertIn('console', handlers, f'{logger_name} does not log to console')
            self.assertIn('log_file', handlers, f'{logger_name} does not log to disk')

    def test_root_logger(self):
        """Test the configuration of the root logger"""

        config = Settings().get_logging_config()
        logger_name = ''  # The root logger is represented in python by an empty string

        self.assertIn(logger_name, config['loggers'], f'{logger_name} has no configuration')

        handlers = config['loggers'][logger_name]['handlers']
        self.assertIn('console', handlers, f'{logger_name} does not log to console')
        self.assertIn('log_file', handlers, f'{logger_name} does not log to disk')
