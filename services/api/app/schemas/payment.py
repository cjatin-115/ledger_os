from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    """Input for recording a supplier payment."""

    supplier_id: UUID

    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    payment_method: str = Field(
        min_length=1,
        max_length=30,
    )

    payment_date: date

    reference_number: str | None = Field(
        default=None,
        max_length=100,
    )

    cheque_number: str | None = Field(
        default=None,
        max_length=50,
    )

    cheque_date: date | None = None

    bank_name: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None


class PaymentAllocationCreate(BaseModel):
    """Input for applying a payment to a bill."""

    bill_id: UUID

    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
    )


class PaymentResponse(BaseModel):
    """Payment returned by the API."""

    id: UUID
    organization_id: UUID
    supplier_id: UUID
    amount: Decimal
    payment_method: str
    payment_date: date
    reference_number: str | None
    cheque_number: str | None
    cheque_date: date | None
    bank_name: str | None
    status: str
    notes: str | None

    model_config = {
        "from_attributes": True,
    }


class PaymentAllocationResponse(BaseModel):
    """Payment allocation returned by the API."""

    id: UUID
    payment_id: UUID
    bill_id: UUID
    amount: Decimal

    model_config = {
        "from_attributes": True,
    }