"""Object relational mapper for the application database."""

from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy

__db_version__ = '0.1'  # Schema version used to track/manage DB migrations
db = SQLAlchemy()


# Table classes are wrapped as dataclasses and all fields are type hinted.
# This allows Flask to automatically serialize table rows into JSON responses

@dataclass
class Pipeline(db.Model):
    """Metadata table for Egon pipelines

    Table Fields:
      - id         (Integer): Primary key for this table
      - egon_id        (str): Unique pipeline ID used by Egon
      - name        (String): Human readable pipeline name
      - description (String): Description of the pipeline function
    """

    __tablename__ = 'pipeline'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    egon_id: str = db.Column(db.String, nullable=False, unique=True)
    name: str = db.Column(db.String, nullable=False)
    description: str = db.Column(db.String, nullable=True)


@dataclass
class Node(db.Model):
    """Metadata for Egon pipeline nodes

    Table Fields:
      - id         (Integer): Primary key for this table
      - egon_id        (str): Unique Node ID used by Egon
      - name        (String): Human readable node name
      - description (String): Description of the node's function
    """

    __tablename__ = 'node'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    egon_id: str = db.Column(db.String, nullable=False, unique=True)
    name: str = db.Column(db.String, nullable=False)
    description: str = db.Column(db.String, nullable=True)
