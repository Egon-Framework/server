"""Tests for the ``auth`` module"""

from unittest import IsolatedAsyncioTestCase

from egon_server import SETTINGS, orm
from egon_server.auth import User


class RegisterCredential(IsolatedAsyncioTestCase):
    """Test the ``register_credential`` method"""

    test_credential = User('test_user')

    async def asyncSetUp(self) -> None:
        """Set up the database connection and delete any existing dummy credentials"""

        orm.DBConnection.configure(SETTINGS.get_db_uri())
        await self.asyncTearDown()

    async def asyncTearDown(self) -> None:
        """Delete any dummy database credentials"""

        await self.test_credential.delete_credential()

    async def test_credential_is_created(self) -> None:
        """Test credentials are created and validate"""

        await self.test_credential.register_credential('password_123!')
        self.assertTrue(await self.test_credential.verify_credential('password_123!'))

    async def test_credentials_recreated(self) -> None:
        """Test the creation of credentials for a previously deleted username"""

        await self.test_credential.register_credential('password_123!')
        await self.test_credential.delete_credential()
        await self.test_credential.register_credential('password_123!')
        self.assertTrue(await self.test_credential.verify_credential('password_123!'))

    async def test_error_existing_credential(self) -> None:
        """Test an error is raised when implicitly overwriting existing credentials"""

        await self.test_credential.register_credential('password_123!')
        with self.assertRaises(ValueError):
            await self.test_credential.register_credential('password_123!')

    async def test_credential_overwritten(self) -> None:
        """Test credentials are changed when explicitly overwritten"""

        await self.test_credential.register_credential('old_password')
        await self.test_credential.register_credential('new_password', overwrite=True)
        self.assertTrue(await self.test_credential.verify_credential('new_password'))


class DeleteCredential(IsolatedAsyncioTestCase):
    """Test the ``delete_credential`` method"""

    async def asyncSetUp(self) -> None:
        """Set up the database connection"""

        orm.DBConnection.configure(SETTINGS.get_db_uri())

    async def test_credentials_are_deleted(self) -> None:
        """Tests deleted credentials no longer validate as true"""

        credential = User('test_user')
        password = 'password_123!'

        await credential.register_credential(password)
        await credential.delete_credential()
        self.assertFalse(await credential.verify_credential(password))

    @staticmethod
    async def test_delete_missing_credentials() -> None:
        """Test no error is raised when deleting usernames that do not exist"""

        credential = User('test_user')
        await credential.delete_credential()
        await credential.delete_credential()


class VerifyCredentials(IsolatedAsyncioTestCase):
    """Test the ``verify_credential`` method"""

    test_credential = User('test_user')

    async def asyncSetUp(self) -> None:
        """Set up the database connection and delete any existing dummy credentials"""

        orm.DBConnection.configure(SETTINGS.get_db_uri())
        await self.asyncTearDown()

    async def asyncTearDown(self) -> None:
        """Delete any dummy database credentials"""

        await self.test_credential.delete_credential()

    async def test_valid_credentials(self) -> None:
        """Test valid credentials validate successfully"""

        await self.test_credential.register_credential('password_123!')
        self.assertTrue(await self.test_credential.verify_credential('password_123!'))

    async def test_invalid_credentials(self) -> None:
        """Test invalid credentials do not validate"""

        await self.test_credential.register_credential('password_123!')
        self.assertFalse(await self.test_credential.verify_credential('not_the_password'))
