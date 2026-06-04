"""add_device_login_geo_observations

Revision ID: o0p1q2r3s4t5
Revises: n9o0p1q2r3s4
Create Date: 2026-05-28 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "o0p1q2r3s4t5"
down_revision: Union[str, Sequence[str], None] = "n9o0p1q2r3s4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_login_geo_observations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("peer_id", sa.Integer(), nullable=True),
        sa.Column("public_ip", sa.String(length=45), nullable=False),
        sa.Column("country_code", sa.String(length=8), nullable=True),
        sa.Column("country_name", sa.String(length=128), nullable=True),
        sa.Column("region_name", sa.String(length=128), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="enroll"),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["peer_id"], ["vpn_peers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_device_login_geo_observations_device_id",
        "device_login_geo_observations",
        ["device_id"],
    )
    op.create_index(
        "ix_device_login_geo_observations_country_code",
        "device_login_geo_observations",
        ["country_code"],
    )
    op.create_index(
        "ix_device_login_geo_observations_observed_at",
        "device_login_geo_observations",
        ["observed_at"],
    )
    op.create_index(
        "ix_device_login_geo_device_observed",
        "device_login_geo_observations",
        ["device_id", "observed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_device_login_geo_device_observed", table_name="device_login_geo_observations")
    op.drop_index("ix_device_login_geo_observations_observed_at", table_name="device_login_geo_observations")
    op.drop_index("ix_device_login_geo_observations_country_code", table_name="device_login_geo_observations")
    op.drop_index("ix_device_login_geo_observations_device_id", table_name="device_login_geo_observations")
    op.drop_table("device_login_geo_observations")
