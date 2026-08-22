from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ExtractedPayment(BaseModel):
    supplier_name: str | None = None
    supplier_id: str | None = None
    amount: Decimal | None = None
    payment_method: str = "upi"
    payment_date: date | None = None
    reference_number: str | None = None
    paid_at: str | None = None
    confidence: Decimal = Decimal("0.00")
    warnings: list[str] = Field(default_factory=list)


class PaymentAllocationSummary(BaseModel):
    bill_id: str
    bill_number: str
    amount: str
    bill_status: str
    outstanding_after: str


class PaymentScanConfirmResponse(BaseModel):
    payment_id: str
    supplier_id: str
    supplier_name: str
    amount: str
    allocated_amount: str
    unallocated_amount: str
    allocations: list[PaymentAllocationSummary]
