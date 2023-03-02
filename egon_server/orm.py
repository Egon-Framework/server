"""Object relational mapper for the application database."""

from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy

__db_version__ = '0.1'

db = SQLAlchemy()


class Pipeline(db.Model):
    """Metadata for a running pipeline

    Table Fields:
      - id         (db.Integer): Primary key for this table
      - name        (String): Human readable pipeline name
      - description (String): Description of the pipeline function
    """

    __tablename__ = 'pipeline'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)


@dataclass
class Node(db.Model):
    """Metadata for a pipeline node

    Table Fields:
      - id         (db.Integer): Primary key for this table
      - name        (String): Human readable node name
      - description (String): Description of the node's function
    """

    __tablename__ = 'node'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
