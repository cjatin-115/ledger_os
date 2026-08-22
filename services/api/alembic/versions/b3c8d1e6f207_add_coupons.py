"""add coupons

Revision ID: b3c8d1e6f207
Revises: a2b7c9d4e105
Create Date: 2026-08-22 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b3c8d1e6f207"
down_revision: Union[str, Sequence[str], None] = "a2b7c9d4e105"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "coupons",
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("plan_code", sa.String(50), nullable=False),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("redemption_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("code"),
    )
    op.create_table(
        "coupon_redemptions",
        sa.Column("coupon_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("redeemed_by", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["coupon_id"], ["coupons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["redeemed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("coupon_id", "organization_id"),
    )
    op.execute(sa.text("INSERT INTO subscription_plans (id, code, name, max_devices) VALUES (gen_random_uuid(), 'shop_unlimited', 'Shop Unlimited', 2147483647)"))
    op.execute(sa.text("INSERT INTO coupons (id, code, plan_code, max_redemptions) VALUES (gen_random_uuid(), 'LEDGEROS-SHOP-UNLIMITED-2026', 'shop_unlimited', 1)"))

def downgrade() -> None:
    op.drop_table("coupon_redemptions")
    op.drop_table("coupons")