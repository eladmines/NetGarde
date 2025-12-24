"""create_blocked_sites_table

Revision ID: 6fd8d677dfc2
Revises: e8f7eb0a723a
Create Date: 2025-11-20 21:14:18.698455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fd8d677dfc2'
down_revision: Union[str, Sequence[str], None] = 'e8f7eb0a723a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old rules table if it exists
    try:
        op.drop_index(op.f('ix_rules_id'), table_name='rules')
        op.drop_index(op.f('ix_rules_domain'), table_name='rules')
        op.drop_table('rules')
    except Exception:
        # Table might not exist, continue
        pass
    
    # Create new blocked_sites table
    op.create_table('blocked_sites',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(), nullable=True),
    sa.Column('reason', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blocked_sites_domain'), 'blocked_sites', ['domain'], unique=True)
    op.create_index(op.f('ix_blocked_sites_id'), 'blocked_sites', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop blocked_sites table
    op.drop_index(op.f('ix_blocked_sites_id'), table_name='blocked_sites')
    op.drop_index(op.f('ix_blocked_sites_domain'), table_name='blocked_sites')
    op.drop_table('blocked_sites')
    
    # Recreate old rules table
    op.create_table('rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(), nullable=True),
    sa.Column('reason', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rules_domain'), 'rules', ['domain'], unique=True)
    op.create_index(op.f('ix_rules_id'), 'rules', ['id'], unique=False)
