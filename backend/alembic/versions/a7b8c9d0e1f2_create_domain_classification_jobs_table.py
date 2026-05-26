"""create_domain_classification_jobs_table

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-03-02 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domain_classification_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_domain_classification_jobs_id"), "domain_classification_jobs", ["id"], unique=False)
    op.create_index(
        op.f("ix_domain_classification_jobs_domain"),
        "domain_classification_jobs",
        ["domain"],
        unique=True,
    )
    op.create_index(op.f("ix_domain_classification_jobs_status"), "domain_classification_jobs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_domain_classification_jobs_status"), table_name="domain_classification_jobs")
    op.drop_index(op.f("ix_domain_classification_jobs_domain"), table_name="domain_classification_jobs")
    op.drop_index(op.f("ix_domain_classification_jobs_id"), table_name="domain_classification_jobs")
    op.drop_table("domain_classification_jobs")

