from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.role import Role


class User(UUIDMixin, TimestampMixin, Base):
    """Represents a user belonging to a LedgerOS organization."""

    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint(
            "email",
            name="uq_users_email",
        ),
        Index(
            "ix_users_organization_id",
            "organization_id",
        ),
        Index(
            "ix_users_role_id",
            "role_id",
        ),
        Index(
            "ix_users_phone_number",
            "phone_number",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )

    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    mfa_secret: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    role: Mapped["Role"] = relationship()
