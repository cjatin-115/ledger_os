from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.supplier import Supplier


class SupplierRepository:
    """Database operations for suppliers."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        supplier: Supplier,
    ) -> Supplier:
        """Persist a new supplier."""

        self.db.add(supplier)
        await self.db.flush()
        await self.db.refresh(supplier)

        return supplier

    async def get_by_id(
        self,
        supplier_id: UUID,
        organization_id: UUID,
    ) -> Supplier | None:
        """Get one supplier belonging to an organization."""

        result = await self.db.execute(
            select(Supplier).where(
                Supplier.id == supplier_id,
                Supplier.organization_id == organization_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_gstin(
        self,
        gstin: str,
        organization_id: UUID,
    ) -> Supplier | None:
        """Find a supplier by GSTIN within an organization."""

        result = await self.db.execute(
            select(Supplier).where(
                Supplier.gstin == gstin,
                Supplier.organization_id == organization_id,
            )
        )

        return result.scalar_one_or_none()

    async def list(
        self,
        organization_id: UUID,
    ) -> list[Supplier]:
        """List all active suppliers for an organization."""

        result = await self.db.execute(
            select(Supplier)
            .where(
                Supplier.organization_id == organization_id,
                Supplier.is_active.is_(True),
            )
            .order_by(Supplier.name.asc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        supplier: Supplier,
    ) -> Supplier:
        """Persist changes to an existing supplier."""

        await self.db.flush()
        await self.db.refresh(supplier)

        return supplier
