from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.bill import Bill
    from app.db.models.user import User


class BillAdjustmentType(StrEnum):
    """Types of financial adjustments that can affect a supplier bill."""

    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    RETURN = "return"
    DISCOUNT = "discount"
    OTHER = "other"


class BillAdjustment(UUIDMixin, CreatedAtMixin, Base):
    """Represents an adjustment applied to a supplier bill."""

    __tablename__ = "bill_adjustments"

    __table_args__ = (
        Index(
            "ix_bill_adjustments_bill_id",
            "bill_id",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_bill_adjustments_amount_positive",
        ),
    )

    bill_id: Mapped[UUID] = mapped_column(
        ForeignKey("bills.id", ondelete="CASCADE"),
        nullable=False,
    )

    adjustment_type: Mapped[BillAdjustmentType] = mapped_column(
        String(30),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    bill: Mapped["Bill"] = relationship(
        back_populates="adjustments",
    )

    creator: Mapped["User"] = relationship()
