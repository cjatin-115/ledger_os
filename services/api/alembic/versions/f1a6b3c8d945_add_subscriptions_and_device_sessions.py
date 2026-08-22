"""add subscriptions and device sessions

Revision ID: f1a6b3c8d945
Revises: e0f5a2b7c934
Create Date: 2026-08-22 02:20:00.000000

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "f1a6b3c8d945"
down_revision: Union[str, Sequence[str], None] = "e0f5a2b7c934"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription_plans",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("max_devices", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "organization_subscriptions",
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("plan_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="active", nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["subscription_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_org_subscriptions_organization_id", "organization_subscriptions", ["organization_id"])
    op.create_table(
        "device_sessions",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=False),
        sa.Column("device_name", sa.String(length=255), nullable=True),
        sa.Column("last_ip", sa.String(length=64), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_device_sessions_user_id", "device_sessions", ["user_id"])
    op.create_index("ix_device_sessions_device_id", "device_sessions", ["user_id", "device_id"])
    op.add_column(
        "refresh_tokens",
        sa.Column("device_session_id", sa.UUID(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            INSERT INTO device_sessions
                (id, user_id, device_id, last_seen_at, is_active, created_at, updated_at)
            SELECT id, user_id, 'legacy-' || id::text, created_at, true, created_at, created_at
            FROM refresh_tokens
            """
        )
    )
    op.execute(
        sa.text(
            "UPDATE refresh_tokens SET device_session_id = id"
        )
    )
    op.alter_column("refresh_tokens", "device_session_id", nullable=False)
    op.create_foreign_key(
        "fk_refresh_tokens_device_session_id",
        "refresh_tokens",
        "device_sessions",
        ["device_session_id"],
        ["id"],
        ondelete="CASCADE",
    )
    starter_id = str(uuid4())
    growth_id = str(uuid4())
    op.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, code, name, max_devices)
            VALUES
                (CAST(:starter_id AS uuid), 'starter', 'Starter', 2),
                (CAST(:growth_id AS uuid), 'growth', 'Growth', 5)
            """
        ).bindparams(starter_id=starter_id, growth_id=growth_id)
    )
    op.execute(
        sa.text(
            """
            INSERT INTO organization_subscriptions
                (id, organization_id, plan_id, status, starts_at)
            SELECT gen_random_uuid(), organizations.id, CAST(:starter_id AS uuid),
                   'active', now()
            FROM organizations
            WHERE NOT EXISTS (
                SELECT 1 FROM organization_subscriptions
                WHERE organization_subscriptions.organization_id = organizations.id
            )
            """
        ).bindparams(starter_id=starter_id)
    )


def downgrade() -> None:
    op.drop_constraint("fk_refresh_tokens_device_session_id", "refresh_tokens", type_="foreignkey")
    op.drop_column("refresh_tokens", "device_session_id")
    op.drop_index("ix_device_sessions_device_id", table_name="device_sessions")
    op.drop_index("ix_device_sessions_user_id", table_name="device_sessions")
    op.drop_table("device_sessions")
    op.drop_index("ix_org_subscriptions_organization_id", table_name="organization_subscriptions")
    op.drop_table("organization_subscriptions")
    op.drop_table("subscription_plans")