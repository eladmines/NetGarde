"""add_vpn_enroll_events

Revision ID: g1h2i3j4k5l6
Revises: f7g8h9i0j1k2
Create Date: 2026-05-02 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "g1h2i3j4k5l6"
down_revision: Union[str, Sequence[str], None] = "f7g8h9i0j1k2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vpn_enroll_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("peer_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=32), nullable=False, server_default="enroll"),
        sa.Column("lease_ip", sa.String(length=45), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("mac_address", sa.String(length=17), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["peer_id"], ["vpn_peers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vpn_enroll_events_id"), "vpn_enroll_events", ["id"], unique=False)
    op.create_index(op.f("ix_vpn_enroll_events_peer_id"), "vpn_enroll_events", ["peer_id"], unique=False)
    op.create_index(op.f("ix_vpn_enroll_events_device_id"), "vpn_enroll_events", ["device_id"], unique=False)
    op.create_index(op.f("ix_vpn_enroll_events_created_at"), "vpn_enroll_events", ["created_at"], unique=False)
    op.create_index(
        "ix_vpn_enroll_events_peer_created_at",
        "vpn_enroll_events",
        ["peer_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_vpn_enroll_events_device_created_at",
        "vpn_enroll_events",
        ["device_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_vpn_enroll_events_device_created_at", table_name="vpn_enroll_events")
    op.drop_index("ix_vpn_enroll_events_peer_created_at", table_name="vpn_enroll_events")
    op.drop_index(op.f("ix_vpn_enroll_events_created_at"), table_name="vpn_enroll_events")
    op.drop_index(op.f("ix_vpn_enroll_events_device_id"), table_name="vpn_enroll_events")
    op.drop_index(op.f("ix_vpn_enroll_events_peer_id"), table_name="vpn_enroll_events")
    op.drop_index(op.f("ix_vpn_enroll_events_id"), table_name="vpn_enroll_events")
    op.drop_table("vpn_enroll_events")

