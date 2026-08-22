from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class AttachmentEntityType(StrEnum):
    """Entity types that can have uploaded attachments."""

    BILL = "bill"
    PAYMENT = "payment"
    SUPPLIER = "supplier"
    BILL_ADJUSTMENT = "bill_adjustment"


class Attachment(UUIDMixin, CreatedAtMixin, Base):
    """Stores metadata for a file attached to a LedgerOS entity."""

    __tablename__ = "attachments"

    __table_args__ = (
        Index(
            "ix_attachments_organization_id",
            "organization_id",
        ),
        Index(
            "ix_attachments_entity",
            "entity_type",
            "entity_id",
        ),
        Index(
            "ix_attachments_uploaded_by",
            "uploaded_by",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )

    entity_type: Mapped[AttachmentEntityType] = mapped_column(
        String(30),
        nullable=False,
    )

    entity_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        nullable=False,
    )

    uploaded_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    uploader: Mapped["User"] = relationship()