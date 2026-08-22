from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.payment import Payment


class PaymentRepository:
    """Database operations for supplier payments."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        payment: Payment,
    ) -> Payment:
        """Persist a payment."""

        self.db.add(payment)
        await self.db.flush()

        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.allocations),
            )
            .where(Payment.id == payment.id)
        )

        return result.scalar_one()

    async def get_by_id(
        self,
        payment_id: UUID,
        organization_id: UUID,
        for_update: bool = False,
    ) -> Payment | None:
        """Get a payment within an organization."""

        statement = (
            select(Payment)
            .options(
                selectinload(Payment.allocations),
            )
            .where(
                Payment.id == payment_id,
                Payment.organization_id == organization_id,
            )
        )
        if for_update:
            statement = statement.with_for_update()

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def list(
        self,
        organization_id: UUID,
    ) -> list[Payment]:
        """List payments belonging to an organization."""

        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.allocations),
            )
            .where(
                Payment.organization_id == organization_id,
            )
            .order_by(Payment.payment_date.desc())
        )

        return list(result.scalars().all())