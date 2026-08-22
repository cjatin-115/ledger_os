from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.payment_allocation import PaymentAllocation


class PaymentAllocationRepository:
    """Database operations for payment allocations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        allocation: PaymentAllocation,
    ) -> PaymentAllocation:
        """Persist a payment allocation."""

        self.db.add(allocation)
        await self.db.flush()

        return allocation

    async def get_total_allocated(
        self,
        payment_id: UUID,
    ) -> object:
        """Return total amount allocated to a payment."""

        from sqlalchemy import func

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(PaymentAllocation.amount),
                    0,
                )
            ).where(
                PaymentAllocation.payment_id == payment_id,
            )
        )

        return result.scalar_one()

    async def get_total_allocated_to_bill(
        self,
        bill_id: UUID,
    ) -> object:
        """Return total payments allocated to a bill."""

        from sqlalchemy import func

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(PaymentAllocation.amount),
                    0,
                )
            ).where(
                PaymentAllocation.bill_id == bill_id,
            )
        )

        return result.scalar_one()
