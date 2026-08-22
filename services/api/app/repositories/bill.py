from datetime import date
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
        for_update: bool = False,
    ) -> Bill | None:
        """Get a bill and its items within an organization."""

        statement = (
            select(Bill)
            .options(
                selectinload(Bill.items),
            )
            .where(
                Bill.id == bill_id,
                Bill.organization_id == organization_id,
            )
        )
        if for_update:
            statement = statement.with_for_update()

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_number(
        self,
        supplier_id: UUID,
        organization_id: UUID,
        bill_number: str,
    ) -> Bill | None:
        """Find a bill by supplier invoice number."""

        result = await self.db.execute(
            select(Bill).where(
                Bill.organization_id == organization_id,
                Bill.supplier_id == supplier_id,
                Bill.bill_number == bill_number,
            )
        )

        return result.scalar_one_or_none()

    async def list(
        self,
        organization_id: UUID,
        search: str | None = None,
        status: str | None = None,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Bill]:
        """List bills belonging to an organization."""

        statement = (
            select(Bill)
            .options(
                selectinload(Bill.items),
                selectinload(Bill.supplier),
            )
            .where(
                Bill.organization_id == organization_id,
            )
        )
        if search:
            statement = statement.where(Bill.bill_number.ilike(f"%{search.strip()}%"))
        if status:
            statement = statement.where(Bill.status == status)
        if due_before:
            statement = statement.where(Bill.due_date <= due_before)
        if due_after:
            statement = statement.where(Bill.due_date >= due_after)
        result = await self.db.execute(statement.order_by(Bill.bill_date.desc()))

        return list(result.scalars().all())

    async def list_for_supplier(
        self,
        organization_id: UUID,
        supplier_id: UUID,
    ) -> "list[Bill]":
        result = await self.db.execute(
            select(Bill).where(
                Bill.organization_id == organization_id,
                Bill.supplier_id == supplier_id,
            )
        )
        return list(result.scalars().all())
