from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class DueReminderResponse(BaseModel):
    bill_id: UUID
    supplier_id: UUID
    bill_number: str
    due_date: date
    days_until_due: int
    outstanding_amount: Decimal
