"""add ipa notes is_important to vocabulary

Revision ID: a1b2c3d4e5f6
Revises: d7f1ed4224d5
Create Date: 2026-07-08 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd7f1ed4224d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vocabularies', sa.Column('ipa', sa.String(), nullable=True))
    op.add_column('vocabularies', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('vocabularies', sa.Column('is_important', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('vocabularies', 'is_important')
    op.drop_column('vocabularies', 'notes')
    op.drop_column('vocabularies', 'ipa')
