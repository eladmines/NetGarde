"""add_rollup_country_counts

Revision ID: m8n9o0p1q2r3
Revises: l7m8n9o0p1q2
Create Date: 2026-06-04 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "m8n9o0p1q2r3"
down_revision: Union[str, Sequence[str], None] = "l7m8n9o0p1q2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "client_behavior_rollups",
        sa.Column("country_counts_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("client_behavior_rollups", "country_counts_json")
