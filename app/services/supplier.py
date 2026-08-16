from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.supplier import Supplier
from app.repositories.supplier import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierService:
    """Business logic for suppliers."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = SupplierRepository(db)

    async def create(
        self,
        payload: SupplierCreate,
        organization_id: UUID,
    ) -> Supplier:
        name = payload.name.strip()

        if not name:
            raise ValueError("Supplier name cannot be blank.")

        gstin = (
            payload.gstin.strip().upper()
            if payload.gstin
            else None
        )

        if gstin:
            existing = await self.repository.get_by_gstin(
                gstin=gstin,
                organization_id=organization_id,
            )

            if existing:
                raise ValueError(
                    "A supplier with this GSTIN already exists."
                )

        supplier = Supplier(
            organization_id=organization_id,
            name=name,
            contact_person=(
                payload.contact_person.strip()
                if payload.contact_person
                else None
            ),
            phone=(
                payload.phone.strip()
                if payload.phone
                else None
            ),
            email=(
                str(payload.email).strip().lower()
                if payload.email
                else None
            ),
            gstin=gstin,
            address=(
                payload.address.strip()
                if payload.address
                else None
            ),
            payment_terms_days=payload.payment_terms_days,
        )

        try:
            supplier = await self.repository.create(supplier)
            await self.db.commit()
            return supplier
        except Exception:
            await self.db.rollback()
            raise

    async def list(
        self,
        organization_id: UUID,
    ) -> list[Supplier]:
        return await self.repository.list(
            organization_id=organization_id,
        )

    async def get(
        self,
        supplier_id: UUID,
        organization_id: UUID,
    ) -> Supplier | None:
        return await self.repository.get_by_id(
            supplier_id=supplier_id,
            organization_id=organization_id,
        )

    async def update(
        self,
        supplier_id: UUID,
        payload: SupplierUpdate,
        organization_id: UUID,
    ) -> Supplier | None:
        supplier = await self.repository.get_by_id(
            supplier_id=supplier_id,
            organization_id=organization_id,
        )

        if supplier is None:
            return None

        data = payload.model_dump(exclude_unset=True)

        if "name" in data:
            name = data["name"].strip()

            if not name:
                raise ValueError("Supplier name cannot be blank.")

            supplier.name = name

        if "contact_person" in data:
            supplier.contact_person = (
                data["contact_person"].strip()
                if data["contact_person"]
                else None
            )

        if "phone" in data:
            supplier.phone = (
                data["phone"].strip()
                if data["phone"]
                else None
            )

        if "email" in data:
            supplier.email = (
                str(data["email"]).strip().lower()
                if data["email"]
                else None
            )

        if "gstin" in data:
            gstin = (
                data["gstin"].strip().upper()
                if data["gstin"]
                else None
            )

            if gstin:
                existing = await self.repository.get_by_gstin(
                    gstin=gstin,
                    organization_id=organization_id,
                )

                if existing and existing.id != supplier.id:
                    raise ValueError(
                        "A supplier with this GSTIN already exists."
                    )

            supplier.gstin = gstin

        if "address" in data:
            supplier.address = (
                data["address"].strip()
                if data["address"]
                else None
            )

        if "payment_terms_days" in data:
            supplier.payment_terms_days = data["payment_terms_days"]

        if "is_active" in data:
            supplier.is_active = data["is_active"]

        try:
            supplier = await self.repository.update(supplier)
            await self.db.commit()
            return supplier
        except Exception:
            await self.db.rollback()
            raise