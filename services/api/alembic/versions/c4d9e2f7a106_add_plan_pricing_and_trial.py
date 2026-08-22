"""add plan pricing and free trial

Revision ID: c4d9e2f7a106
Revises: b3c8d1e6f207
Create Date: 2026-08-22 03:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c4d9e2f7a106"
down_revision: Union[str, Sequence[str], None] = "b3c8d1e6f207"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subscription_plans",
        sa.Column("price_per_device", sa.Numeric(12, 2), server_default="0", nullable=False),
    )
    op.add_column(
        "subscription_plans",
        sa.Column("currency", sa.String(3), server_default="INR", nullable=False),
    )
    op.add_column(
        "subscription_plans",
        sa.Column("billing_interval", sa.String(20), server_default="monthly", nullable=False),
    )
    op.add_column(
        "subscription_plans",
        sa.Column("trial_days", sa.Integer(), server_default="0", nullable=False),
    )
    op.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price_per_device = CASE
                    WHEN code = 'growth' THEN 99
                    ELSE 0
                END,
                currency = 'INR',
                billing_interval = 'monthly'
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO subscription_plans
                (id, code, name, max_devices, price_per_device, currency,
                 billing_interval, trial_days)
            VALUES
                (gen_random_uuid(), 'free_trial', 'Free Trial', 2, 0,
                 'INR', 'monthly', 14)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO subscription_plans
                (id, code, name, max_devices, price_per_device, currency,
                 billing_interval, trial_days)
            VALUES
                (gen_random_uuid(), 'pro', 'Pro', 5, 99,
                 'INR', 'monthly', 0)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.drop_column("subscription_plans", "trial_days")
    op.drop_column("subscription_plans", "billing_interval")
    op.drop_column("subscription_plans", "currency")
    op.drop_column("subscription_plans", "price_per_device")