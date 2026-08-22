from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_organization_id, require_permission
from app.db.models.organization_subscription import OrganizationSubscription
from app.db.models.subscription_plan import SubscriptionPlan
from app.db.session import get_db
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    SubscriptionResponse,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
) -> list[SubscriptionPlanResponse]:
    result = await db.execute(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active.is_(True))
        .order_by(SubscriptionPlan.price_per_device)
    )
    return [
        SubscriptionPlanResponse.model_validate(plan) for plan in result.scalars().all()
    ]


@router.get("/current", response_model=SubscriptionResponse)
async def current_subscription(
    organization_id: UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("auth.me")),
) -> SubscriptionResponse:
    result = await db.execute(
        select(OrganizationSubscription)
        .options(selectinload(OrganizationSubscription.plan))
        .where(OrganizationSubscription.organization_id == organization_id)
        .order_by(OrganizationSubscription.created_at.desc())
        .limit(1)
    )
    subscription = result.scalar_one()
    return SubscriptionResponse(
        plan=SubscriptionPlanResponse.model_validate(subscription.plan),
        status=subscription.status,
        starts_at=subscription.starts_at,
        ends_at=subscription.ends_at,
    )
