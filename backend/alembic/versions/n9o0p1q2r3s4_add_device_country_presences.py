"""add_device_country_presences

Revision ID: n9o0p1q2r3s4
Revises: m8n9o0p1q2r3
Create Date: 2026-06-04 14:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "n9o0p1q2r3s4"
down_revision: Union[str, Sequence[str], None] = "m8n9o0p1q2r3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_country_presences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("country_code", sa.String(length=8), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("query_count", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "country_code", name="uq_device_country_presence"),
    )
    op.create_index(
        "ix_device_country_presences_device_id",
        "device_country_presences",
        ["device_id"],
    )
    op.create_index(
        "ix_device_country_presences_country_code",
        "device_country_presences",
        ["country_code"],
    )


def downgrade() -> None:
    op.drop_index("ix_device_country_presences_country_code", table_name="device_country_presences")
    op.drop_index("ix_device_country_presences_device_id", table_name="device_country_presences")
    op.drop_table("device_country_presences")
