from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class LedgerTransactionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    supplier_id: UUID
    transaction_type: str
    reference_type: str
    reference_id: UUID
    debit_amount: Decimal
    credit_amount: Decimal
    transaction_date: date
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReconciliationResponse(BaseModel):
    transaction_count: int
    total_debits: Decimal
    total_credits: Decimal
    net_balance: Decimal
    balanced: bool