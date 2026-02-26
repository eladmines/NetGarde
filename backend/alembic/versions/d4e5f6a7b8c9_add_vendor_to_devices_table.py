"""add_vendor_to_devices_table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-02-26 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("devices", sa.Column("vendor", sa.String(length=100), nullable=True))
    op.create_index(op.f("ix_devices_vendor"), "devices", ["vendor"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_devices_vendor"), table_name="devices")
    op.drop_column("devices", "vendor")
