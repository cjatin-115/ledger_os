from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.supplier import Supplier


class AccountTransactionType(StrEnum):
    """Financial events that affect the supplier payable ledger."""

    OPENING_BALANCE = "opening_balance"
    BILL = "bill"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    DISCOUNT = "discount"
    PAYMENT = "payment"


class AccountTransaction(UUIDMixin, CreatedAtMixin, Base):
    """Represents an immutable financial event in a supplier ledger."""

    __tablename__ = "account_transactions"

    __table_args__ = (
        Index(
            "ix_account_transactions_organization_id",
            "organization_id",
        ),
        Index(
            "ix_account_transactions_supplier_id",
            "supplier_id",
        ),
        Index(
            "ix_account_transactions_transaction_date",
            "transaction_date",
        ),
        Index(
            "ix_account_transactions_reference",
            "reference_type",
            "reference_id",
        ),
        CheckConstraint(
            "debit_amount >= 0",
            name="ck_account_transactions_debit_non_negative",
        ),
        CheckConstraint(
            "credit_amount >= 0",
            name="ck_account_transactions_credit_non_negative",
        ),
        CheckConstraint(
            "(debit_amount > 0 AND credit_amount = 0) "
            "OR (debit_amount = 0 AND credit_amount > 0)",
            name="ck_account_transactions_one_sided",
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

    transaction_type: Mapped[AccountTransactionType] = mapped_column(
        String(30),
        nullable=False,
    )

    reference_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    reference_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    debit_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    credit_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0",
    )

    transaction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    supplier: Mapped["Supplier"] = relationship()