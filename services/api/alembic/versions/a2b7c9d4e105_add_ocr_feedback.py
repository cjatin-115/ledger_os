"""add ocr correction feedback

Revision ID: a2b7c9d4e105
Revises: f1a6b3c8d945
Create Date: 2026-08-22 02:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a2b7c9d4e105"
down_revision: Union[str, Sequence[str], None] = "f1a6b3c8d945"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ocr_correction_feedback",
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("bill_id", sa.UUID(), nullable=True),
        sa.Column("corrected_by", sa.UUID(), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("ocr_value", sa.Text(), nullable=False),
        sa.Column("final_value", sa.Text(), nullable=False),
        sa.Column("ocr_numeric_value", sa.Numeric(14, 2), nullable=True),
        sa.Column("final_numeric_value", sa.Numeric(14, 2), nullable=True),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["bill_id"], ["bills.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["corrected_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ocr_feedback_organization_id", "ocr_correction_feedback", ["organization_id"])
    op.create_index("ix_ocr_feedback_bill_id", "ocr_correction_feedback", ["bill_id"])


def downgrade() -> None:
    op.drop_index("ix_ocr_feedback_bill_id", table_name="ocr_correction_feedback")
    op.drop_index("ix_ocr_feedback_organization_id", table_name="ocr_correction_feedback")
    op.drop_table("ocr_correction_feedback")