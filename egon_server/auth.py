"""Utilities for managing user credentials and server authentication."""

from hashlib import sha256

from sqlalchemy import insert, delete, select
from sqlalchemy.exc import IntegrityError

from . import orm
from .settings import Settings


async def register_credential(name: str, password: str, overwrite: bool = False) -> None:
    """Create/update user credentials in the application database

    Args:
        name: The user/client name
        password: The user/client password
        overwrite: Allow existing credentials to be overwritten

    Raises:
        ValueError: When credentials for the given ``name`` already exist and ``overwrite`` is ``False``.
    """

    async with orm.DBConnection.session_maker() as session:
        # Salt and hash the given password
        salted = password + Settings().secret_key
        hashed = sha256(salted.encode()).hexdigest()

        # Structure the query as an upsert if ``overwrite`` is enables
        query = insert(orm.Client).values(name=name, password=hashed)
        if overwrite:
            query = query.on_conflict_do_update()

        try:
            await session.execute(query)
            await session.commit()

        except IntegrityError as caught:
            raise ValueError('Client credentials already exist.') from caught


async def delete_credential(name: str) -> None:
    """Delete user credentials frm the application database

    Args:
        name: The user/client name
    """

    async with orm.DBConnection.session_maker() as session:
        await session.execute(delete(orm.Client).where(orm.Client.name == name))
        await session.commit()


async def verify_credential(name: str, password: str) -> bool:
    """Verify the given user credentials

    Args:
        name: The user/client name
        password: The user/client password

    Returns:
        Whether the credentials are valid
    """

    salted = password + Settings().secret_key
    hashed = sha256(salted.encode()).hexdigest()

    async with orm.DBConnection.session_maker() as session:
        query = select(orm.Client).where(orm.Client.name == name)
        db_record: orm.Client = await session.execute(query).first()
        return (db_record is not None) and db_record.password == hashed
