"""remove_domain_classification_tables

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_domain_classification_jobs_status"), table_name="domain_classification_jobs")
    op.drop_index(op.f("ix_domain_classification_jobs_domain"), table_name="domain_classification_jobs")
    op.drop_index(op.f("ix_domain_classification_jobs_id"), table_name="domain_classification_jobs")
    op.drop_table("domain_classification_jobs")

    op.drop_index(op.f("ix_domain_categories_category_id"), table_name="domain_categories")
    op.drop_index(op.f("ix_domain_categories_domain"), table_name="domain_categories")
    op.drop_index(op.f("ix_domain_categories_id"), table_name="domain_categories")
    op.drop_table("domain_categories")


def downgrade() -> None:
    raise NotImplementedError("Downgrade is intentionally unsupported for this cleanup migration.")

