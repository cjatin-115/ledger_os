from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class AuditLog(UUIDMixin, CreatedAtMixin, Base):
    """Immutable record of an important action performed in LedgerOS."""

    __tablename__ = "audit_logs"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    actor: Mapped["User | None"] = relationship()