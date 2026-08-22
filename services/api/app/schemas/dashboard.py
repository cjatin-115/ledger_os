from decimal import Decimal

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    suppliers_count: int
    bills_count: int
    open_bills_count: int
    payments_count: int
    billed_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    overdue_amount: Decimal
    due_soon_amount: Decimal
