"""add_blocked_sites_notify_trigger

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-02-27 00:15:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_blocked_sites_changed()
        RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify(
                'blocked_sites_changed',
                json_build_object(
                    'operation', TG_OP,
                    'id', COALESCE(NEW.id, OLD.id),
                    'domain', COALESCE(NEW.domain, OLD.domain),
                    'at', now()
                )::text
            );
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute("DROP TRIGGER IF EXISTS tr_blocked_sites_changed_notify ON blocked_sites;")
    op.execute(
        """
        CREATE TRIGGER tr_blocked_sites_changed_notify
        AFTER INSERT OR UPDATE OR DELETE ON blocked_sites
        FOR EACH ROW
        EXECUTE FUNCTION notify_blocked_sites_changed();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS tr_blocked_sites_changed_notify ON blocked_sites;")
    op.execute("DROP FUNCTION IF EXISTS notify_blocked_sites_changed();")
