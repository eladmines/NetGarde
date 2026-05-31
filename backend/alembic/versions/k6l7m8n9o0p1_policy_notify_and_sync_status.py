"""policy notify trigger and sync status

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-05-28 18:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "k6l7m8n9o0p1"
down_revision: Union[str, Sequence[str], None] = "j5k6l7m8n9o0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "policy_sync_status",
        sa.Column("id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success", sa.Boolean(), nullable=True),
        sa.Column("last_message", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("id = 1", name="ck_policy_sync_status_singleton"),
    )
    op.execute(
        "INSERT INTO policy_sync_status (id, last_sync_at, last_success, last_message) VALUES (1, NULL, NULL, NULL)"
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_policy_changed()
        RETURNS trigger AS $$
        DECLARE
            payload json;
        BEGIN
            payload := json_build_object(
                'operation', TG_OP,
                'table', TG_TABLE_NAME,
                'at', now()
            );
            IF TG_TABLE_NAME = 'policy_packs' THEN
                payload := payload || json_build_object(
                    'slug', COALESCE(NEW.slug, OLD.slug),
                    'enabled_globally', COALESCE(NEW.enabled_globally, OLD.enabled_globally)
                );
            ELSIF TG_TABLE_NAME = 'policy_profiles' THEN
                payload := payload || json_build_object(
                    'slug', COALESCE(NEW.slug, OLD.slug)
                );
            ELSIF TG_TABLE_NAME = 'devices' THEN
                payload := payload || json_build_object(
                    'device_id', COALESCE(NEW.id, OLD.id),
                    'policy_profile_id', COALESCE(NEW.policy_profile_id, OLD.policy_profile_id)
                );
            END IF;
            PERFORM pg_notify('policy_changed', payload::text);
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    for table, sql in (
        (
            "policy_packs",
            """
            CREATE TRIGGER tr_policy_packs_policy_changed_notify
            AFTER UPDATE OF enabled_globally ON policy_packs
            FOR EACH ROW
            WHEN (OLD.enabled_globally IS DISTINCT FROM NEW.enabled_globally)
            EXECUTE FUNCTION notify_policy_changed();
            """,
        ),
        (
            "policy_profiles",
            """
            CREATE TRIGGER tr_policy_profiles_policy_changed_notify
            AFTER UPDATE ON policy_profiles
            FOR EACH ROW
            EXECUTE FUNCTION notify_policy_changed();
            """,
        ),
        (
            "devices",
            """
            CREATE TRIGGER tr_devices_policy_changed_notify
            AFTER INSERT OR UPDATE OF policy_profile_id OR DELETE ON devices
            FOR EACH ROW
            EXECUTE FUNCTION notify_policy_changed();
            """,
        ),
    ):
        op.execute(f"DROP TRIGGER IF EXISTS tr_{table}_policy_changed_notify ON {table};")
        op.execute(sql)


def downgrade() -> None:
    for table in ("devices", "policy_profiles", "policy_packs"):
        op.execute(f"DROP TRIGGER IF EXISTS tr_{table}_policy_changed_notify ON {table};")
    op.execute("DROP FUNCTION IF EXISTS notify_policy_changed();")
    op.drop_table("policy_sync_status")
