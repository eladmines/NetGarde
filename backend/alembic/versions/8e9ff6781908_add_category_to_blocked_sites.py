"""add_category_to_blocked_sites

Revision ID: 8e9ff6781908
Revises: 6fd8d677dfc2
Create Date: 2025-11-21 12:57:23.493462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e9ff6781908'
down_revision: Union[str, Sequence[str], None] = '6fd8d677dfc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('blocked_sites', sa.Column('category', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('blocked_sites', 'category')
