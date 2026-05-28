"""create_domain_categories_table

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-03-02 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domain_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domain", "category_id", name="uq_domain_categories_domain_category_id"),
    )
    op.create_index(op.f("ix_domain_categories_id"), "domain_categories", ["id"], unique=False)
    op.create_index(op.f("ix_domain_categories_domain"), "domain_categories", ["domain"], unique=False)
    op.create_index(op.f("ix_domain_categories_category_id"), "domain_categories", ["category_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_domain_categories_category_id"), table_name="domain_categories")
    op.drop_index(op.f("ix_domain_categories_domain"), table_name="domain_categories")
    op.drop_index(op.f("ix_domain_categories_id"), table_name="domain_categories")
    op.drop_table("domain_categories")

