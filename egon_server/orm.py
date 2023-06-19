"""Object relational mapper for the application database."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from requests import Session
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

__db_version__ = '0.1'  # Schema version used to track/manage DB migrations
MIGRATIONS_DIR = Path(__file__).parent / 'migrations'

Base = declarative_base()


class DBConnection:
    """A configurable connection to the application database

    This class acts as the primary interface for connecting to the application
    database. Use the ``configure`` method to change the location of the
    underlying application database. Changes made via this class will
    propagate to the entire parent application.
    """

    engine: Optional[AsyncEngine] = None
    connection: Optional[Connection] = None
    session_maker: Optional[Callable[[], Session]] = None

    @classmethod
    def configure(cls, url: str) -> None:
        """Update the connection information for the underlying database

        Changes made here will affect the entire running application

        Args:
            url: URL information for the application database
        """

        if cls.connection:
            cls.connection.close()

        cls.connection = None
        cls.engine = create_async_engine(url)
        cls.session_maker = sessionmaker(cls.engine, class_=AsyncSession)


@dataclass
class Client(Base):
    """Client machine authentication data

    Table Fields:
      - id      (Integer): Primary key for this table
      - name     (String): Client name
      - password (String): Hashed client passwrd
    """

    __tablename__ = 'client'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable=False, unique=True, index=True)
    password: str = Column(String, nullable=False)


@dataclass
class Pipeline(Base):
    """Metadata table for Egon pipelines

    Table Fields:
      - id         (Integer): Primary key for this table
      - egon_id     (String): Unique pipeline ID used by Egon
      - name        (String): Human readable pipeline name
      - description (String): Description of the pipeline function
      - last_updated  (Date): The last time the record was updated
    """

    __tablename__ = 'pipeline'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    egon_id: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=True)
    last_updated: datetime = Column(DateTime(timezone=True), nullable=False, default=func.now())


@dataclass
class Node(Base):
    """Metadata for Egon pipeline nodes

    Table Fields:
      - id         (Integer): Primary key for this table
      - egon_id     (String): Unique Node ID used by Egon
      - name        (String): Human readable node name
      - description (String): Description of the node's function
      - last_updated  (Date): The last time the record was updated
    """

    __tablename__ = 'node'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    egon_id: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=True)
    last_updated: datetime = Column(DateTime(timezone=True), nullable=False, default=func.now())
