from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.bill import Bill


class BillRepository:
    """Database operations for supplier bills."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        bill: Bill,
    ) -> Bill:
        """Persist a bill and return it with its items loaded."""

        self.db.add(bill)

        await self.db.flush()

        result = await self.db.execute(
            select(Bill)
            .options(
                selectinload(Bill.items),
            )
            .where(Bill.id == bill.id)
        )

        created_bill = result.scalar_one()

        return created_bill

    async def get_by_id(
        self,
        bill_id: UUID,
        organization_id: UUID,
    ) -> Bill | None:
        """Get a bill and its items within an organization."""

        result = await self.db.execute(
            select(Bill)
            .options(
                selectinload(Bill.items),
            )
            .where(
                Bill.id == bill_id,
                Bill.organization_id == organization_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_number(
        self,
        supplier_id: UUID,
        organization_id: UUID,
        bill_number: str,
    ) -> Bill | None:
        """Find a bill by supplier invoice number."""

        result = await self.db.execute(
            select(Bill)
            .where(
                Bill.organization_id == organization_id,
                Bill.supplier_id == supplier_id,
                Bill.bill_number == bill_number,
            )
        )

        return result.scalar_one_or_none()

    async def list(
        self,
        organization_id: UUID,
    ) -> list[Bill]:
        """List bills belonging to an organization."""

        result = await self.db.execute(
            select(Bill)
            .options(
                selectinload(Bill.items),
            )
            .where(
                Bill.organization_id == organization_id,
            )
            .order_by(Bill.bill_date.desc())
        )

        return list(result.scalars().all())