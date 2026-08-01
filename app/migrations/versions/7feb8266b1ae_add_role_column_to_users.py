"""Add role column to users

Revision ID: 7feb8266b1ae
Revises: d83e9c02e76f
Create Date: 2026-07-06 01:54:44.831749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '7feb8266b1ae'
down_revision: Union[str, Sequence[str], None] = 'd83e9c02e76f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role = ENUM('admin', 'user', name='user_role', create_type=True)
    user_role.create(op.get_bind())
    op.add_column('users', sa.Column('role', user_role, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    op.execute("DROP TYPE user_role")
