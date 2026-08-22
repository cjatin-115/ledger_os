from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class SubscriptionPlanResponse(BaseModel):
    id: UUID
    code: str
    name: str
    max_devices: int
    price_per_device: Decimal
    currency: str
    billing_interval: str
    trial_days: int

    model_config = {"from_attributes": True}


class SubscriptionResponse(BaseModel):
    plan: SubscriptionPlanResponse
    status: str
    starts_at: datetime
    ends_at: datetime | None