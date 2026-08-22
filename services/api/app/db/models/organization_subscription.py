from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.organization import Organization
    from app.db.models.subscription_plan import SubscriptionPlan


class OrganizationSubscription(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organization_subscriptions"

    __table_args__ = (Index("ix_org_subscriptions_organization_id", "organization_id"),)

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscription_plans.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", server_default="active")
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship()
    plan: Mapped["SubscriptionPlan"] = relationship()
