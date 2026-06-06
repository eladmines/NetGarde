"""add_geo_country_blocks

Revision ID: p1q2r3s4t5u6
Revises: o0p1q2r3s4t5
Create Date: 2026-05-29 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "p1q2r3s4t5u6"
down_revision: Union[str, Sequence[str], None] = "o0p1q2r3s4t5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "geo_country_policy_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("configured_in_ui", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("vpn_login_block_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("destination_rules_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        "INSERT INTO geo_country_policy_config "
        "(id, configured_in_ui, vpn_login_block_enabled, destination_rules_enabled, updated_at) "
        "VALUES (1, false, true, true, CURRENT_TIMESTAMP)"
    )

    op.create_table(
        "geo_country_blocks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("block_type", sa.String(length=32), nullable=False),
        sa.Column("user_country_code", sa.String(length=2), nullable=True),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "block_type",
            "user_country_code",
            "country_code",
            name="uq_geo_country_blocks_type_user_dest",
        ),
    )
    op.create_index("ix_geo_country_blocks_block_type", "geo_country_blocks", ["block_type"])


def downgrade() -> None:
    op.drop_index("ix_geo_country_blocks_block_type", table_name="geo_country_blocks")
    op.drop_table("geo_country_blocks")
    op.drop_table("geo_country_policy_config")
