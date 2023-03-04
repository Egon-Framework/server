"""Migrates database to schema version 0.1."""

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision = '0.1'
down_revision = None
branch_labels = ('default',)
depends_on = None


def upgrade() -> None:
    """Upgrade from previous database versions to the current revision"""

    op.create_table(
        'node',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('egon_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'pipeline',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('egon_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'))


def downgrade() -> None:
    """Downgrade from the current database versions to the previous revision"""

    raise RuntimeError('There is no revision below this version to revert to.')
