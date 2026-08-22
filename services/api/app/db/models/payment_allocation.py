from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.bill import Bill
    from app.db.models.payment import Payment


class PaymentAllocation(UUIDMixin, CreatedAtMixin, Base):
    """Represents part of a payment applied to a specific bill."""

    __tablename__ = "payment_allocations"

    __table_args__ = (
        Index(
            "ix_payment_allocations_payment_id",
            "payment_id",
        ),
        Index(
            "ix_payment_allocations_bill_id",
            "bill_id",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_payment_allocations_amount_positive",
        ),
    )

    payment_id: Mapped[UUID] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
    )

    bill_id: Mapped[UUID] = mapped_column(
        ForeignKey("bills.id"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    payment: Mapped["Payment"] = relationship(
        back_populates="allocations",
    )

    bill: Mapped["Bill"] = relationship(
        back_populates="allocations",
    )