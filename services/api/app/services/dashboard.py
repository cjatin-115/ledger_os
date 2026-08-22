from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.bill import Bill, BillStatus
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.payment_allocation import PaymentAllocation
from app.db.models.supplier import Supplier
from app.schemas.dashboard import DashboardSummaryResponse


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def summary(
        self,
        organization_id: UUID,
    ) -> DashboardSummaryResponse:
        allocation_totals = (
            select(
                PaymentAllocation.bill_id.label("bill_id"),
                func.coalesce(
                    func.sum(PaymentAllocation.amount),
                    Decimal("0.00"),
                ).label("allocated_amount"),
            )
            .group_by(PaymentAllocation.bill_id)
            .subquery()
        )
        bill_balance = func.coalesce(
            allocation_totals.c.allocated_amount,
            Decimal("0.00"),
        )
        bill_outstanding = Bill.total_amount - bill_balance
        active_bill = Bill.status != BillStatus.CANCELLED

        supplier_count = await self.db.scalar(
            select(func.count(Supplier.id)).where(
                Supplier.organization_id == organization_id,
                Supplier.is_active.is_(True),
            )
        )
        bill_count = await self.db.scalar(
            select(func.count(Bill.id)).where(
                Bill.organization_id == organization_id,
                active_bill,
            )
        )
        open_bill_count = await self.db.scalar(
            select(func.count(Bill.id))
            .outerjoin(
                allocation_totals,
                allocation_totals.c.bill_id == Bill.id,
            )
            .where(
                Bill.organization_id == organization_id,
                active_bill,
                bill_outstanding > 0,
            )
        )
        payment_count = await self.db.scalar(
            select(func.count(Payment.id)).where(
                Payment.organization_id == organization_id,
                Payment.status == PaymentStatus.RECORDED,
            )
        )
        billed_amount = await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Bill.total_amount),
                    Decimal("0.00"),
                )
            ).where(
                Bill.organization_id == organization_id,
                active_bill,
            )
        )
        paid_amount = await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Payment.amount),
                    Decimal("0.00"),
                )
            ).where(
                Payment.organization_id == organization_id,
                Payment.status == PaymentStatus.RECORDED,
            )
        )
        outstanding_amount = await self._sum_outstanding(
            organization_id,
            allocation_totals,
            bill_outstanding,
            active_bill,
        )
        overdue_amount = await self._sum_outstanding(
            organization_id,
            allocation_totals,
            bill_outstanding,
            active_bill,
            Bill.due_date < date.today(),
        )
        due_soon_amount = await self._sum_outstanding(
            organization_id,
            allocation_totals,
            bill_outstanding,
            active_bill,
            Bill.due_date >= date.today(),
            Bill.due_date <= date.today() + timedelta(days=7),
        )

        return DashboardSummaryResponse(
            suppliers_count=int(supplier_count or 0),
            bills_count=int(bill_count or 0),
            open_bills_count=int(open_bill_count or 0),
            payments_count=int(payment_count or 0),
            billed_amount=billed_amount or Decimal("0.00"),
            paid_amount=paid_amount or Decimal("0.00"),
            outstanding_amount=outstanding_amount,
            overdue_amount=overdue_amount,
            due_soon_amount=due_soon_amount,
        )

    async def _sum_outstanding(
        self,
        organization_id: UUID,
        allocation_totals,
        bill_outstanding,
        active_bill,
        *conditions,
    ) -> Decimal:
        result = await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(bill_outstanding),
                    Decimal("0.00"),
                )
            )
            .outerjoin(
                allocation_totals,
                allocation_totals.c.bill_id == Bill.id,
            )
            .where(
                Bill.organization_id == organization_id,
                active_bill,
                bill_outstanding > 0,
                *conditions,
            )
        )
        return result or Decimal("0.00")