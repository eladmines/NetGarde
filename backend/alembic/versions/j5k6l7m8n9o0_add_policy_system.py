"""add_policy_system

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-05-28 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "j5k6l7m8n9o0"
down_revision: Union[str, Sequence[str], None] = "i4j5k6l7m8n9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "policy_packs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled_globally", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_policy_packs_slug", "policy_packs", ["slug"], unique=True)

    op.create_table(
        "policy_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled_pack_slugs", sa.JSON(), nullable=False),
        sa.Column("extra_block_domains", sa.JSON(), nullable=False),
        sa.Column("allowlist_domains", sa.JSON(), nullable=False),
        sa.Column("schedule_rules", sa.JSON(), nullable=False),
        sa.Column("behavior_sensitivity", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("quarantine_on_abnormal", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("quarantine_hours", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_policy_profiles_slug", "policy_profiles", ["slug"], unique=True)

    op.create_table(
        "device_quarantines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_device_quarantines_device_id", "device_quarantines", ["device_id"])
    op.create_index("ix_device_quarantines_expires_at", "device_quarantines", ["expires_at"])

    op.add_column("devices", sa.Column("policy_profile_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_devices_policy_profile_id",
        "devices",
        "policy_profiles",
        ["policy_profile_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_devices_policy_profile_id", "devices", ["policy_profile_id"])

    packs = sa.table(
        "policy_packs",
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("enabled_globally", sa.Boolean),
    )
    op.bulk_insert(
        packs,
        [
            {"slug": "adult", "name": "Adult", "description": "Adult content sites", "enabled_globally": False},
            {"slug": "gambling", "name": "Gambling", "description": "Gambling and betting", "enabled_globally": False},
            {"slug": "malware", "name": "Malware", "description": "Known malicious and ad-tracker domains", "enabled_globally": True},
            {"slug": "social", "name": "Social", "description": "Social networks", "enabled_globally": False},
            {"slug": "games", "name": "Games", "description": "Gaming platforms", "enabled_globally": False},
        ],
    )

    bedtime = [
        {
            "days": [0, 1, 2, 3, 4, 5, 6],
            "start": "22:00",
            "end": "07:00",
            "pack_slugs": ["social", "games"],
        }
    ]
    profiles = sa.table(
        "policy_profiles",
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("enabled_pack_slugs", sa.JSON),
        sa.column("extra_block_domains", sa.JSON),
        sa.column("allowlist_domains", sa.JSON),
        sa.column("schedule_rules", sa.JSON),
        sa.column("behavior_sensitivity", sa.String),
        sa.column("quarantine_on_abnormal", sa.Boolean),
        sa.column("quarantine_hours", sa.Integer),
        sa.column("is_builtin", sa.Boolean),
    )
    op.bulk_insert(
        profiles,
        [
            {
                "slug": "kids",
                "name": "Kids",
                "description": "Strict filtering with bedtime social/games block",
                "enabled_pack_slugs": ["adult", "gambling", "malware", "social", "games"],
                "extra_block_domains": [],
                "allowlist_domains": ["google.com", "wikipedia.org", "khanacademy.org"],
                "schedule_rules": bedtime,
                "behavior_sensitivity": "high",
                "quarantine_on_abnormal": True,
                "quarantine_hours": 6,
                "is_builtin": True,
            },
            {
                "slug": "teen",
                "name": "Teen",
                "description": "Adult/gambling blocked; social limited at night",
                "enabled_pack_slugs": ["adult", "gambling", "malware"],
                "extra_block_domains": [],
                "allowlist_domains": [],
                "schedule_rules": bedtime,
                "behavior_sensitivity": "medium",
                "quarantine_on_abnormal": True,
                "quarantine_hours": 4,
                "is_builtin": True,
            },
            {
                "slug": "work",
                "name": "Work",
                "description": "Malware only; relaxed behavior scoring",
                "enabled_pack_slugs": ["malware"],
                "extra_block_domains": [],
                "allowlist_domains": [],
                "schedule_rules": [],
                "behavior_sensitivity": "low",
                "quarantine_on_abnormal": False,
                "quarantine_hours": 2,
                "is_builtin": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_devices_policy_profile_id", table_name="devices")
    op.drop_constraint("fk_devices_policy_profile_id", "devices", type_="foreignkey")
    op.drop_column("devices", "policy_profile_id")
    op.drop_index("ix_device_quarantines_expires_at", table_name="device_quarantines")
    op.drop_index("ix_device_quarantines_device_id", table_name="device_quarantines")
    op.drop_table("device_quarantines")
    op.drop_index("ix_policy_profiles_slug", table_name="policy_profiles")
    op.drop_table("policy_profiles")
    op.drop_index("ix_policy_packs_slug", table_name="policy_packs")
    op.drop_table("policy_packs")
