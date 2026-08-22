from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class Supplier(UUIDMixin, TimestampMixin, Base):
    """Represents a supplier belonging to a LedgerOS organization."""

    __tablename__ = "suppliers"

    __table_args__ = (
        Index(
            "ix_suppliers_organization_id",
            "organization_id",
        ),
        Index(
            "uq_suppliers_organization_gstin",
            "organization_id",
            "gstin",
            unique=True,
            postgresql_where=text("gstin IS NOT NULL"),
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    gstin: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    payment_terms_days: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
