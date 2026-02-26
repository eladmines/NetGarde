"""create_devices_table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-26 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_ip", sa.String(length=45), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("mac_address", sa.String(length=17), nullable=True),
        sa.Column("vendor", sa.String(length=100), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="manual"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_devices_id"), "devices", ["id"], unique=False)
    op.create_index(op.f("ix_devices_client_ip"), "devices", ["client_ip"], unique=True)
    op.create_index(op.f("ix_devices_hostname"), "devices", ["hostname"], unique=False)
    op.create_index(op.f("ix_devices_mac_address"), "devices", ["mac_address"], unique=True)
    op.create_index(op.f("ix_devices_vendor"), "devices", ["vendor"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_devices_mac_address"), table_name="devices")
    op.drop_index(op.f("ix_devices_hostname"), table_name="devices")
    op.drop_index(op.f("ix_devices_client_ip"), table_name="devices")
    op.drop_index(op.f("ix_devices_vendor"), table_name="devices")
    op.drop_index(op.f("ix_devices_id"), table_name="devices")
    op.drop_table("devices")
