from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.bill import Bill


class BillItem(UUIDMixin, TimestampMixin, Base):
    """Represents one line item on a supplier bill."""

    __tablename__ = "bill_items"

    __table_args__ = (
        Index(
            "ix_bill_items_bill_id",
            "bill_id",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_bill_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_bill_items_unit_price_non_negative",
        ),
        CheckConstraint(
            "discount_amount >= 0",
            name="ck_bill_items_discount_non_negative",
        ),
        CheckConstraint(
            "discount_amount <= quantity * unit_price",
            name="ck_bill_items_discount_not_greater_than_gross",
        ),
        CheckConstraint(
            "tax_rate >= 0 AND tax_rate <= 100",
            name="ck_bill_items_tax_rate_valid",
        ),
        CheckConstraint(
            "tax_amount >= 0",
            name="ck_bill_items_tax_non_negative",
        ),
        CheckConstraint(
            "line_total >= 0",
            name="ck_bill_items_line_total_non_negative",
        ),
    )

    bill_id: Mapped[UUID] = mapped_column(
        ForeignKey("bills.id", ondelete="CASCADE"),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PCS",
        server_default="PCS",
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    line_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    hsn_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    bill: Mapped["Bill"] = relationship(
        back_populates="items",
    )
