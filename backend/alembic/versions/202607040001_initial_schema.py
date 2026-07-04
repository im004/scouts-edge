"""initial schema

Revision ID: 202607040001
Revises:
Create Date: 2026-07-04
"""

from alembic import op

from app.db.base import Base

revision = "202607040001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
