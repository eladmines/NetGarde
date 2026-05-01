"""create_ip_pools_and_leases

Revision ID: d1e2f3a4b5c6
Revises: c9d0e1f2a3b4
Create Date: 2026-05-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ip_pools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("cidr", sa.String(length=43), nullable=False),
        sa.Column("gateway_ip", sa.String(length=45), nullable=False),
        sa.Column("dns_ip", sa.String(length=45), nullable=False),
        sa.Column("mtu", sa.Integer(), nullable=True),
        sa.Column("allowed_ips", sa.String(length=400), nullable=True),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("server_public_key", sa.String(length=255), nullable=False),
        sa.Column("persistent_keepalive", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ip_pools_id"), "ip_pools", ["id"], unique=False)
    op.create_index(op.f("ix_ip_pools_name"), "ip_pools", ["name"], unique=True)

    op.create_table(
        "vpn_peers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("public_key", sa.String(length=255), nullable=False),
        sa.Column("pool_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["pool_id"], ["ip_pools.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vpn_peers_id"), "vpn_peers", ["id"], unique=False)
    op.create_index(op.f("ix_vpn_peers_device_id"), "vpn_peers", ["device_id"], unique=True)
    op.create_index(op.f("ix_vpn_peers_public_key"), "vpn_peers", ["public_key"], unique=True)
    op.create_index(op.f("ix_vpn_peers_pool_id"), "vpn_peers", ["pool_id"], unique=False)

    op.create_table(
        "ip_leases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pool_id", sa.Integer(), nullable=False),
        sa.Column("peer_id", sa.Integer(), nullable=False),
        sa.Column("ip", sa.String(length=45), nullable=False),
        sa.Column("leased_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["peer_id"], ["vpn_peers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["pool_id"], ["ip_pools.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pool_id", "ip", name="uq_ip_leases_pool_ip"),
        sa.UniqueConstraint("peer_id", name="uq_ip_leases_peer_id"),
    )
    op.create_index(op.f("ix_ip_leases_id"), "ip_leases", ["id"], unique=False)
    op.create_index(op.f("ix_ip_leases_pool_id"), "ip_leases", ["pool_id"], unique=False)
    op.create_index(op.f("ix_ip_leases_peer_id"), "ip_leases", ["peer_id"], unique=False)
    op.create_index("ix_ip_leases_pool_active", "ip_leases", ["pool_id", "released_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ip_leases_pool_active", table_name="ip_leases")
    op.drop_index(op.f("ix_ip_leases_peer_id"), table_name="ip_leases")
    op.drop_index(op.f("ix_ip_leases_pool_id"), table_name="ip_leases")
    op.drop_index(op.f("ix_ip_leases_id"), table_name="ip_leases")
    op.drop_table("ip_leases")

    op.drop_index(op.f("ix_vpn_peers_pool_id"), table_name="vpn_peers")
    op.drop_index(op.f("ix_vpn_peers_public_key"), table_name="vpn_peers")
    op.drop_index(op.f("ix_vpn_peers_device_id"), table_name="vpn_peers")
    op.drop_index(op.f("ix_vpn_peers_id"), table_name="vpn_peers")
    op.drop_table("vpn_peers")

    op.drop_index(op.f("ix_ip_pools_name"), table_name="ip_pools")
    op.drop_index(op.f("ix_ip_pools_id"), table_name="ip_pools")
    op.drop_table("ip_pools")

