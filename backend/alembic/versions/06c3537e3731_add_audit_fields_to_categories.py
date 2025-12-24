"""add_audit_fields_to_categories

Revision ID: 06c3537e3731
Revises: ca500d9f3677
Create Date: 2025-11-21 13:41:59.782876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06c3537e3731'
down_revision: Union[str, Sequence[str], None] = 'ca500d9f3677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if columns exist before adding them (PostgreSQL)
    conn = op.get_bind()
    
    # Check and add created_by
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='categories' AND column_name='created_by'"
    ))
    if not result.fetchone():
        op.add_column('categories', sa.Column('created_by', sa.Integer(), nullable=True))
    
    # Check and add updated_by
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='categories' AND column_name='updated_by'"
    ))
    if not result.fetchone():
        op.add_column('categories', sa.Column('updated_by', sa.Integer(), nullable=True))
    
    # Check and add is_deleted
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='categories' AND column_name='is_deleted'"
    ))
    if not result.fetchone():
        op.add_column('categories', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove audit columns
    op.drop_column('categories', 'is_deleted')
    op.drop_column('categories', 'updated_by')
    op.drop_column('categories', 'created_by')
