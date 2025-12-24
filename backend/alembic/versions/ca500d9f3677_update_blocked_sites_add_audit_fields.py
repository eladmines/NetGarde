"""update_blocked_sites_add_audit_fields

Revision ID: ca500d9f3677
Revises: fdf2c999cd82
Create Date: 2025-11-21 13:25:41.945848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca500d9f3677'
down_revision: Union[str, Sequence[str], None] = 'fdf2c999cd82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop deleted_at column
    op.drop_column('blocked_sites', 'deleted_at')
    
    # Add new audit columns
    op.add_column('blocked_sites', sa.Column('created_by', sa.Integer(), nullable=True))
    op.add_column('blocked_sites', sa.Column('updated_by', sa.Integer(), nullable=True))
    op.add_column('blocked_sites', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove new audit columns
    op.drop_column('blocked_sites', 'is_deleted')
    op.drop_column('blocked_sites', 'updated_by')
    op.drop_column('blocked_sites', 'created_by')
    
    # Restore deleted_at column
    op.add_column('blocked_sites', sa.Column('deleted_at', sa.DateTime(), nullable=True))
