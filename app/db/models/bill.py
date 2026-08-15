from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.bill_adjustment import BillAdjustment
    from app.db.models.bill_item import BillItem


class BillStatus(StrEnum):
    """Valid lifecycle states for a supplier bill."""

    DRAFT = "draft"
    POSTED = "posted"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"


class BillSourceType(StrEnum):
    """How a bill entered the LedgerOS system."""

    MANUAL = "manual"
    IMAGE = "image"
    PDF = "pdf"
    IMPORT = "import"
    WHATSAPP = "whatsapp"


class Bill(UUIDMixin, TimestampMixin, Base):
    """Represents an incoming supplier bill."""

    __tablename__ = "bills"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )

    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
    )

    bill_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    bill_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    taxable_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    cgst_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    sgst_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    igst_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    status: Mapped[BillStatus] = mapped_column(
        String(30),
        nullable=False,
        default=BillStatus.DRAFT,
        server_default=BillStatus.DRAFT.value,
    )

    source_type: Mapped[BillSourceType] = mapped_column(
        String(30),
        nullable=False,
        default=BillSourceType.MANUAL,
        server_default=BillSourceType.MANUAL.value,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    items: Mapped[list["BillItem"]] = relationship(
        back_populates="bill",
        cascade="all, delete-orphan",
    )

    adjustments: Mapped[list["BillAdjustment"]] = relationship(
        back_populates="bill",
        cascade="all, delete-orphan",
    )