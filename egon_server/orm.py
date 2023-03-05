"""Object relational mapper for the application database."""

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

__db_version__ = '0.1'  # Schema version used to track/manage DB migrations

Base = declarative_base()


@dataclass
class Pipeline(Base):
    """Metadata table for Egon pipelines

    Table Fields:
      - id         (Integer): Primary key for this table
      - egon_id        (str): Unique pipeline ID used by Egon
      - name        (String): Human readable pipeline name
      - description (String): Description of the pipeline function
    """

    __tablename__ = 'pipeline'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    egon_id: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=True)


@dataclass
class Node(Base):
    """Metadata for Egon pipeline nodes

    Table Fields:
      - id         (Integer): Primary key for this table
      - egon_id        (str): Unique Node ID used by Egon
      - name        (String): Human readable node name
      - description (String): Description of the node's function
    """

    __tablename__ = 'node'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    egon_id: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=True)
