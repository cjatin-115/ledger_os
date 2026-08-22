from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.bill import Bill, BillStatus
from app.db.models.payment_allocation import PaymentAllocation
from app.schemas.reminder import DueReminderResponse


class ReminderService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def due_bills(
        self,
        organization_id: UUID,
        days: int = 7,
    ) -> list[DueReminderResponse]:
        allocation_totals = (
            select(
                PaymentAllocation.bill_id.label("bill_id"),
                func.sum(PaymentAllocation.amount).label("allocated"),
            )
            .group_by(PaymentAllocation.bill_id)
            .subquery()
        )
        today = date.today()
        result = await self.db.execute(
            select(
                Bill,
                (Bill.total_amount - func.coalesce(allocation_totals.c.allocated, 0)).label("outstanding"),
            )
            .outerjoin(
                allocation_totals,
                allocation_totals.c.bill_id == Bill.id,
            )
            .where(
                Bill.organization_id == organization_id,
                Bill.status.not_in([BillStatus.CANCELLED, BillStatus.PAID]),
                Bill.due_date.is_not(None),
                Bill.due_date <= date.fromordinal(today.toordinal() + days),
                (Bill.total_amount - func.coalesce(allocation_totals.c.allocated, 0)) > 0,
            )
            .order_by(Bill.due_date)
        )
        return [
            DueReminderResponse(
                bill_id=bill.id,
                supplier_id=bill.supplier_id,
                bill_number=bill.bill_number,
                due_date=bill.due_date,
                days_until_due=(bill.due_date - today).days,
                outstanding_amount=outstanding,
            )
            for bill, outstanding in result.all()
        ]
