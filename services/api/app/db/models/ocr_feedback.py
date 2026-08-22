from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class OCRCorrectionFeedback(UUIDMixin, CreatedAtMixin, Base):
    __tablename__ = "ocr_correction_feedback"

    __table_args__ = (
        Index("ix_ocr_feedback_organization_id", "organization_id"),
        Index("ix_ocr_feedback_bill_id", "bill_id"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    bill_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bills.id", ondelete="SET NULL"), nullable=True
    )
    corrected_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ocr_value: Mapped[str] = mapped_column(Text, nullable=False)
    final_value: Mapped[str] = mapped_column(Text, nullable=False)
    ocr_numeric_value: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    final_numeric_value: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    context: Mapped[str | None] = mapped_column(Text, nullable=True)

    corrected_user: Mapped["User"] = relationship()