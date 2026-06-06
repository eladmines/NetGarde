"""fix_policy_notify_jsonb

Revision ID: l7m8n9o0p1q2
Revises: k6l7m8n9o0p1
Create Date: 2026-05-28 20:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "l7m8n9o0p1q2"
down_revision: Union[str, Sequence[str], None] = "k6l7m8n9o0p1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NOTIFY_FUNCTION = """
CREATE OR REPLACE FUNCTION notify_policy_changed()
RETURNS trigger AS $$
DECLARE
    payload jsonb;
BEGIN
    payload := jsonb_build_object(
        'operation', TG_OP,
        'table', TG_TABLE_NAME,
        'at', now()
    );
    IF TG_TABLE_NAME = 'policy_packs' THEN
        payload := payload || jsonb_build_object(
            'slug', COALESCE(NEW.slug, OLD.slug),
            'enabled_globally', COALESCE(NEW.enabled_globally, OLD.enabled_globally)
        );
    ELSIF TG_TABLE_NAME = 'policy_profiles' THEN
        payload := payload || jsonb_build_object(
            'slug', COALESCE(NEW.slug, OLD.slug)
        );
    ELSIF TG_TABLE_NAME = 'devices' THEN
        payload := payload || jsonb_build_object(
            'device_id', COALESCE(NEW.id, OLD.id),
            'policy_profile_id', COALESCE(NEW.policy_profile_id, OLD.policy_profile_id)
        );
    END IF;
    PERFORM pg_notify('policy_changed', payload::text);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(_NOTIFY_FUNCTION)


def downgrade() -> None:
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
