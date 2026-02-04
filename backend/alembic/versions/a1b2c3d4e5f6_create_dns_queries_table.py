"""create_dns_queries_table

Revision ID: a1b2c3d4e5f6
Revises: 06c3537e3731
Create Date: 2026-02-04 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '06c3537e3731'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create dns_queries table for logging DNS activity."""
    op.create_table('dns_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('client_ip', sa.String(45), nullable=False),  # IPv6 max length
        sa.Column('domain', sa.String(255), nullable=False),
        sa.Column('query_type', sa.String(10), nullable=True),  # A, AAAA, MX, etc.
        sa.Column('action', sa.String(20), nullable=True),  # forwarded, blocked, cached
        sa.Column('blocked', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for fast queries
    op.create_index(op.f('ix_dns_queries_id'), 'dns_queries', ['id'], unique=False)
    op.create_index(op.f('ix_dns_queries_timestamp'), 'dns_queries', ['timestamp'], unique=False)
    op.create_index(op.f('ix_dns_queries_domain'), 'dns_queries', ['domain'], unique=False)
    op.create_index(op.f('ix_dns_queries_client_ip'), 'dns_queries', ['client_ip'], unique=False)
    op.create_index(op.f('ix_dns_queries_blocked'), 'dns_queries', ['blocked'], unique=False)


def downgrade() -> None:
    """Drop dns_queries table."""
    op.drop_index(op.f('ix_dns_queries_blocked'), table_name='dns_queries')
    op.drop_index(op.f('ix_dns_queries_client_ip'), table_name='dns_queries')
    op.drop_index(op.f('ix_dns_queries_domain'), table_name='dns_queries')
    op.drop_index(op.f('ix_dns_queries_timestamp'), table_name='dns_queries')
    op.drop_index(op.f('ix_dns_queries_id'), table_name='dns_queries')
    op.drop_table('dns_queries')
