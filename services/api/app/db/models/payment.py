from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.payment_allocation import PaymentAllocation


class PaymentMethod(StrEnum):
    """Methods through which a supplier payment can be made."""

    CASH = "cash"
    UPI = "upi"
    CHEQUE = "cheque"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(StrEnum):
    """Lifecycle states for a supplier payment."""

    RECORDED = "recorded"
    CANCELLED = "cancelled"


class Payment(UUIDMixin, CreatedAtMixin, Base):
    """Represents money paid to a supplier."""

    __tablename__ = "payments"

    __table_args__ = (
        Index(
            "ix_payments_organization_id",
            "organization_id",
        ),
        Index(
            "ix_payments_supplier_id",
            "supplier_id",
        ),
        Index(
            "ix_payments_payment_date",
            "payment_date",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_payments_amount_positive",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )

    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    payment_method: Mapped[PaymentMethod] = mapped_column(
        String(30),
        nullable=False,
    )

    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    cheque_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    cheque_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    bank_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[PaymentStatus] = mapped_column(
        String(20),
        nullable=False,
        default=PaymentStatus.RECORDED,
        server_default=PaymentStatus.RECORDED.value,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    allocations: Mapped[list["PaymentAllocation"]] = relationship(
        back_populates="payment",
        cascade="all, delete-orphan",
    )