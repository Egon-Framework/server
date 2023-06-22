"""Utilities for managing user credentials and server authentication."""

from __future__ import annotations

from datetime import timedelta, datetime
from typing import Literal

from jose import jwt
from passlib.hash import bcrypt
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from . import orm, SETTINGS


class User:
    """Credential management for individual userf accounts"""

    def __init__(self, username: str) -> None:
        """Manage credentials for a given username

        Args:
            username: Username to manage credentials for
        """

        self._username = username

    @property
    def username(self) -> str:
        """Return th current username being managed"""

        return self._username

    async def register_credential(self, password: str, overwrite: bool = False) -> None:
        """Create/update user credentials in the application database

        Args:
            password: The current user's password
            overwrite: Allow existing credentials to be overwritten

        Raises:
            ValueError: When credentials for the given ``name`` already exist and ``overwrite`` is ``False``.
        """

        async with orm.DBConnection.session_maker() as session:
            credentials = dict(name=self.username, password=bcrypt.hash(password))
            query = insert(orm.Client).values(**credentials)

            # Structure the query as an upsert if ``overwrite`` is enabled
            if overwrite:
                query = query.on_conflict_do_update(index_elements=['name'], set_=credentials)

            try:
                await session.execute(query)
                await session.commit()

            except IntegrityError as caught:
                raise ValueError('Client credentials already exist.') from caught

    async def delete_credential(self) -> None:
        """Delete user credentials from the application database"""

        async with orm.DBConnection.session_maker() as session:
            await session.execute(delete(orm.Client).where(orm.Client.name == self.username))
            await session.commit()

    async def verify_credential(self, password: str) -> bool:
        """Verify the user credentials against a given password

        Args:
            password: The user password

        Returns:
            Whether the credentials are valid
        """

        async with orm.DBConnection.session_maker() as session:
            query = select(orm.Client).where(orm.Client.name == self.username)
            result = await session.execute(query)
            db_record: orm.Client = result.scalars().first()
            return (db_record is not None) and bcrypt.verify(password, db_record.password)


class Scope:
    """An OAuth2 compliant scope"""

    def __init__(self, permission: Literal['read', 'write'], resource: str) -> None:
        """Create a new scope instance

        Args:
            permission: Whether the scope has ``read`` or ``write`` permissions
            resource: The resource UUID the scope applies to
        """

        self.permission = permission
        self.resource = resource

    @classmethod
    def from_string(cls, string: str) -> Scope:
        """Create a new ``Scope`` instance from an OAuth2 compliant scope string"""

        return Scope(*string.split(':'))

    def to_string(self) -> str:
        """Return the current scope as an Auth2 compliant string"""

        return f'{self.permission}:{self.resource}'


class Token:
    """An Oauth2 access token"""

    def __init__(self, token: str) -> None:
        """Create a new token instance

        Args:
            token: An encoded JWT token
        """

        self._token = token

        # See the ``create_token`` for the decoded data model
        token_data = jwt.decode(token, SETTINGS.secret_key, algorithms=['HS256'])
        self._scope: str = token_data['scope']
        self._expires: int = token_data['expires']

    @property
    def encoded(self) -> str:
        """Return the encoded token value"""

        return self._token

    @property
    def scopes(self) -> tuple[Scope]:
        """Return the scopes assigned to the current token"""

        return tuple(Scope.from_string(scp) for scp in ' '.split(self._scope))

    @property
    def expires(self) -> datetime:
        """Return the token expiration datetime in UTC"""

        return datetime.utcfromtimestamp(self._expires)

    def is_expired(self) -> bool:
        """Return if the access token has already expired"""

        return self.expires >= datetime.utcnow()

    @classmethod
    async def create_token(cls, scopes: list[Scope], expires: timedelta | None = None) -> Token:
        """Create a new token instance

        Args:
            scopes: A list of scopes permitted by the token
            expires: Optionally limit how long the token is valid for

        Returns:
            A new ``Token`` instance
        """

        if expires is not None:
            expires = datetime.utcnow() + expires

        oauth_scope = ' '.join(str(scp) for scp in scopes)
        token_data = {'scope': oauth_scope, 'expires': expires}
        encoded_jwt = jwt.encode(token_data, SETTINGS.secret_key, algorithm='HS256')
        return cls(encoded_jwt)
