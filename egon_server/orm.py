from sqlalchemy import Column, Integer, MetaData, String, create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Pipeline(Base):
    """Metadata for a running pipeline

    Table Fields:
      - id         (Integer): Primary key for this table
      - name        (String): Human readable pipeline name
      - description (String): Description of the pipeline function
    """

    __tablename__ = 'pipeline'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


class Node(Base):
    """Metadata for a pipeline node

    Table Fields:
      - id         (Integer): Primary key for this table
      - name        (String): Human readable node name
      - description (String): Description of the node's function
    """

    __tablename__ = 'node'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


class DBConnection:
    """A configurable connection to the application database"""

    connection: Connection = None
    engine: Engine = None
    metadata: MetaData = Base.metadata
    session = None

    @classmethod
    def configure(cls, user: str, password: str, host: str, port: int, database: str) -> None:
        """Update the connection information for the underlying database

        Changes made here are global and affect the entire running application.

        Args:
            user: Username for the database connection
            password: Password for the database connection
            host: Address for the running database host
            port: Port number for accessing the database host
            database: The application database name
        """

        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        cls.engine = create_engine(url)
        cls.metadata.create_all(cls.engine)
        cls.connection = cls.engine.connect()
        cls.session = sessionmaker(cls.engine)
