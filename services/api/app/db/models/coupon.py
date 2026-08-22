from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin, UUIDMixin


class Coupon(UUIDMixin, CreatedAtMixin, Base):
    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan_code: Mapped[str] = mapped_column(String(50), nullable=False)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    redemption_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")


class CouponRedemption(UUIDMixin, CreatedAtMixin, Base):
    __tablename__ = "coupon_redemptions"

    coupon_id: Mapped[UUID] = mapped_column(ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    redeemed_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
