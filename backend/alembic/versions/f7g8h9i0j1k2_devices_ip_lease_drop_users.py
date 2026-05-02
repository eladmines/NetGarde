"""devices_ip_lease_drop_users

Revision ID: f7g8h9i0j1k2
Revises: d1e2f3a4b5c6
Create Date: 2026-05-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7g8h9i0j1k2"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("devices", sa.Column("ip_lease_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_devices_ip_lease_id_ip_leases",
        "devices",
        "ip_leases",
        ["ip_lease_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_devices_ip_lease_id"), "devices", ["ip_lease_id"], unique=False)

    op.execute(
        """
        UPDATE devices AS d
        SET ip_lease_id = il.id
        FROM ip_leases AS il
        WHERE il.ip = d.client_ip AND il.released_at IS NULL
        """
    )

    op.execute("DELETE FROM devices WHERE ip_lease_id IS NULL")

    op.drop_constraint("fk_devices_user_id_users", "devices", type_="foreignkey")
    op.drop_index(op.f("ix_devices_user_id"), table_name="devices")
    op.drop_column("devices", "user_id")

    op.drop_index(op.f("ix_devices_vendor"), table_name="devices")
    op.drop_column("devices", "vendor")

    op.drop_column("devices", "is_active")

    op.drop_index(op.f("ix_devices_client_ip"), table_name="devices")
    op.drop_column("devices", "client_ip")

    op.alter_column("devices", "ip_lease_id", nullable=False)
    op.create_unique_constraint("uq_devices_ip_lease_id", "devices", ["ip_lease_id"])

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_name"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")


def downgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_name"), "users", ["name"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.drop_constraint("uq_devices_ip_lease_id", "devices", type_="unique")

    op.add_column(
        "devices",
        sa.Column("client_ip", sa.String(length=45), nullable=True),
    )
    op.execute(
        """
        UPDATE devices AS d
        SET client_ip = il.ip
        FROM ip_leases AS il
        WHERE il.id = d.ip_lease_id
        """
    )
    op.execute(
        """
        UPDATE devices
        SET client_ip = '10.99.0.' || ((id % 250) + 1)::text
        WHERE client_ip IS NULL
        """
    )
    op.alter_column("devices", "client_ip", existing_type=sa.String(length=45), nullable=False)
    op.create_index(op.f("ix_devices_client_ip"), "devices", ["client_ip"], unique=True)

    op.drop_constraint("fk_devices_ip_lease_id_ip_leases", "devices", type_="foreignkey")
    op.drop_index(op.f("ix_devices_ip_lease_id"), table_name="devices")
    op.drop_column("devices", "ip_lease_id")

    op.add_column("devices", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_devices_user_id"), "devices", ["user_id"], unique=False)
    op.create_foreign_key(
        "fk_devices_user_id_users",
        "devices",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("devices", sa.Column("vendor", sa.String(length=100), nullable=True))
    op.create_index(op.f("ix_devices_vendor"), "devices", ["vendor"], unique=False)

    op.add_column(
        "devices",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
