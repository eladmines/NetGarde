"""add_client_behavior_tables

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-05-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "i4j5k6l7m8n9"
down_revision: Union[str, Sequence[str], None] = "h3i4j5k6l7m8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "client_behavior_rollups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("query_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_roots", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_roots", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hour_utc", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "window_start", name="uq_behavior_rollup_device_window"),
    )
    op.create_index(
        op.f("ix_client_behavior_rollups_device_id"),
        "client_behavior_rollups",
        ["device_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_client_behavior_rollups_window_start"),
        "client_behavior_rollups",
        ["window_start"],
        unique=False,
    )

    op.create_table(
        "client_behavior_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("baseline_json", sa.Text(), nullable=True),
        sa.Column("profile_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_score", sa.Integer(), nullable=True),
        sa.Column("last_scored_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", name="uq_client_behavior_profile_device"),
    )
    op.create_index(
        op.f("ix_client_behavior_profiles_device_id"),
        "client_behavior_profiles",
        ["device_id"],
        unique=True,
    )

    op.create_table(
        "device_security_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("auto_block_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("auto_block_threshold", sa.Integer(), nullable=False, server_default="85"),
        sa.Column("max_blocks_per_day", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", name="uq_device_security_policy_device"),
    )

    op.create_table(
        "client_blocked_domains",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("root_domain", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="behavior_auto"),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "domain", name="uq_client_blocked_device_domain"),
    )
    op.create_index(
        op.f("ix_client_blocked_domains_device_id"),
        "client_blocked_domains",
        ["device_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_client_blocked_domains_expires_at"),
        "client_blocked_domains",
        ["expires_at"],
        unique=False,
    )

    op.add_column("dns_alerts", sa.Column("device_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_dns_alerts_device_id",
        "dns_alerts",
        "devices",
        ["device_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_dns_alerts_device_id"), "dns_alerts", ["device_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_dns_alerts_device_id"), table_name="dns_alerts")
    op.drop_constraint("fk_dns_alerts_device_id", "dns_alerts", type_="foreignkey")
    op.drop_column("dns_alerts", "device_id")

    op.drop_index(op.f("ix_client_blocked_domains_expires_at"), table_name="client_blocked_domains")
    op.drop_index(op.f("ix_client_blocked_domains_device_id"), table_name="client_blocked_domains")
    op.drop_table("client_blocked_domains")

    op.drop_table("device_security_policies")

    op.drop_index(op.f("ix_client_behavior_profiles_device_id"), table_name="client_behavior_profiles")
    op.drop_table("client_behavior_profiles")

    op.drop_index(op.f("ix_client_behavior_rollups_window_start"), table_name="client_behavior_rollups")
    op.drop_index(op.f("ix_client_behavior_rollups_device_id"), table_name="client_behavior_rollups")
    op.drop_table("client_behavior_rollups")
