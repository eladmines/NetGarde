"""add_dns_alerts_and_usage_samples

Revision ID: h3i4j5k6l7m8
Revises: g1h2i3j4k5l6
Create Date: 2026-05-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "h3i4j5k6l7m8"
down_revision: Union[str, Sequence[str], None] = "g1h2i3j4k5l6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dns_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("client_ip", sa.String(length=45), nullable=False),
        sa.Column("alert_type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("root_domain", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dns_alerts_id"), "dns_alerts", ["id"], unique=False)
    op.create_index(op.f("ix_dns_alerts_timestamp"), "dns_alerts", ["timestamp"], unique=False)
    op.create_index(op.f("ix_dns_alerts_client_ip"), "dns_alerts", ["client_ip"], unique=False)
    op.create_index(op.f("ix_dns_alerts_alert_type"), "dns_alerts", ["alert_type"], unique=False)
    op.create_index(op.f("ix_dns_alerts_domain"), "dns_alerts", ["domain"], unique=False)
    op.create_index("ix_dns_alerts_type_ts", "dns_alerts", ["alert_type", "timestamp"], unique=False)

    op.create_table(
        "domain_first_seen",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_ip", sa.String(length=45), nullable=False),
        sa.Column("root_domain", sa.String(length=255), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_ip", "root_domain", name="uq_domain_first_seen_client_root"),
    )
    op.create_index(op.f("ix_domain_first_seen_id"), "domain_first_seen", ["id"], unique=False)
    op.create_index(op.f("ix_domain_first_seen_client_ip"), "domain_first_seen", ["client_ip"], unique=False)
    op.create_index(op.f("ix_domain_first_seen_root_domain"), "domain_first_seen", ["root_domain"], unique=False)

    op.create_table(
        "device_usage_samples",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_external_id", sa.String(length=64), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_sec", sa.Float(), nullable=False),
        sa.Column("rx_bytes", sa.BigInteger(), nullable=False),
        sa.Column("tx_bytes", sa.BigInteger(), nullable=False),
        sa.Column("delta_rx_bytes", sa.BigInteger(), nullable=False),
        sa.Column("delta_tx_bytes", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_device_usage_samples_id"), "device_usage_samples", ["id"], unique=False)
    op.create_index(op.f("ix_device_usage_samples_device_external_id"), "device_usage_samples", ["device_external_id"], unique=False)
    op.create_index(op.f("ix_device_usage_samples_recorded_at"), "device_usage_samples", ["recorded_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_device_usage_samples_recorded_at"), table_name="device_usage_samples")
    op.drop_index(op.f("ix_device_usage_samples_device_external_id"), table_name="device_usage_samples")
    op.drop_index(op.f("ix_device_usage_samples_id"), table_name="device_usage_samples")
    op.drop_table("device_usage_samples")

    op.drop_index(op.f("ix_domain_first_seen_root_domain"), table_name="domain_first_seen")
    op.drop_index(op.f("ix_domain_first_seen_client_ip"), table_name="domain_first_seen")
    op.drop_index(op.f("ix_domain_first_seen_id"), table_name="domain_first_seen")
    op.drop_table("domain_first_seen")

    op.drop_index("ix_dns_alerts_type_ts", table_name="dns_alerts")
    op.drop_index(op.f("ix_dns_alerts_domain"), table_name="dns_alerts")
    op.drop_index(op.f("ix_dns_alerts_alert_type"), table_name="dns_alerts")
    op.drop_index(op.f("ix_dns_alerts_client_ip"), table_name="dns_alerts")
    op.drop_index(op.f("ix_dns_alerts_timestamp"), table_name="dns_alerts")
    op.drop_index(op.f("ix_dns_alerts_id"), table_name="dns_alerts")
    op.drop_table("dns_alerts")
