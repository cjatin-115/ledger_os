from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.payment_extractor import (
    extract_payment_from_image,
    extract_payment_from_text,
)
from app.db.models.bill import Bill, BillStatus
from app.db.models.supplier import Supplier
from app.repositories.bill import BillRepository
from app.repositories.payment_allocation import PaymentAllocationRepository
from app.schemas.payment import PaymentCreate
from app.schemas.payment_extraction import ExtractedPayment
from app.services.payment import PaymentService


class PaymentExtractionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.payment_service = PaymentService(db)
        self.bill_repository = BillRepository(db)
        self.allocation_repository = PaymentAllocationRepository(db)

    async def extract_from_text(
        self,
        raw_text: str,
        organization_id: UUID,
    ) -> ExtractedPayment:
        extracted = extract_payment_from_text(raw_text)
        if extracted.supplier_name:
            supplier = await self._find_supplier_by_name(
                extracted.supplier_name,
                organization_id,
            )
            if supplier:
                extracted = extracted.model_copy(
                    update={"supplier_id": str(supplier.id)}
                )
        return extracted

    async def extract_from_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        organization_id: UUID,
    ) -> ExtractedPayment:
        extracted = extract_payment_from_image(image_bytes, mime_type)
        if extracted.supplier_name:
            supplier = await self._find_supplier_by_name(
                extracted.supplier_name,
                organization_id,
            )
            if supplier:
                extracted = extracted.model_copy(
                    update={"supplier_id": str(supplier.id)}
                )
        return extracted

    async def confirm_extracted_payment(
        self,
        payload: ExtractedPayment,
        organization_id: UUID,
    ) -> dict:
        if payload.amount is None or payload.amount <= 0:
            raise ValueError("A valid payment amount is required.")

        supplier = None
        if payload.supplier_id:
            supplier = await self.db.get(Supplier, UUID(payload.supplier_id))
            if supplier and supplier.organization_id != organization_id:
                supplier = None

        if supplier is None and payload.supplier_name:
            supplier = await self._find_supplier_by_name(
                payload.supplier_name,
                organization_id,
            )

        if supplier is None:
            raise ValueError(
                "Supplier could not be matched. Add the supplier first or pick one manually."
            )

        payment_date = payload.payment_date or date.today()

        payment = await self.payment_service.create(
            PaymentCreate(
                supplier_id=supplier.id,
                amount=payload.amount,
                payment_method=payload.payment_method,
                payment_date=payment_date,
                reference_number=payload.reference_number,
                notes="Created from payment receipt scan",
            ),
            organization_id=organization_id,
        )

        remaining = Decimal(payment.amount)
        allocations: list[dict] = []

        open_bills = await self._list_open_bills(supplier.id, organization_id)

        for bill in open_bills:
            if remaining <= 0:
                break

            allocated_to_bill = (
                await self.allocation_repository.get_total_allocated_to_bill(
                    bill_id=bill.id,
                )
            )
            outstanding = Decimal(bill.total_amount) - Decimal(allocated_to_bill)
            if outstanding <= 0:
                continue

            allocate_amount = min(remaining, outstanding)

            from app.schemas.payment import PaymentAllocationCreate

            await self.payment_service.allocate(
                payment_id=payment.id,
                payload=PaymentAllocationCreate(
                    bill_id=bill.id,
                    amount=allocate_amount,
                ),
                organization_id=organization_id,
            )

            new_outstanding = outstanding - allocate_amount
            allocations.append(
                {
                    "bill_id": str(bill.id),
                    "bill_number": bill.bill_number,
                    "amount": str(allocate_amount.quantize(Decimal("0.01"))),
                    "bill_status": bill.status.value
                    if hasattr(bill.status, "value")
                    else str(bill.status),
                    "outstanding_after": str(new_outstanding.quantize(Decimal("0.01"))),
                }
            )
            remaining -= allocate_amount

        allocated_total = Decimal(payment.amount) - remaining

        return {
            "payment_id": str(payment.id),
            "supplier_id": str(supplier.id),
            "supplier_name": supplier.name,
            "amount": str(Decimal(payment.amount).quantize(Decimal("0.01"))),
            "allocated_amount": str(allocated_total.quantize(Decimal("0.01"))),
            "unallocated_amount": str(remaining.quantize(Decimal("0.01"))),
            "allocations": allocations,
        }

    async def _find_supplier_by_name(
        self,
        name: str,
        organization_id: UUID,
    ) -> Supplier | None:
        normalized = name.strip()
        if not normalized:
            return None

        result = await self.db.execute(
            select(Supplier).where(
                Supplier.organization_id == organization_id,
                func.lower(Supplier.name) == normalized.lower(),
            )
        )
        supplier = result.scalar_one_or_none()
        if supplier:
            return supplier

        result = await self.db.execute(
            select(Supplier).where(
                Supplier.organization_id == organization_id,
                Supplier.name.ilike(f"%{normalized}%"),
            )
        )
        return result.scalars().first()

    async def _list_open_bills(
        self,
        supplier_id: UUID,
        organization_id: UUID,
    ) -> list[Bill]:
        result = await self.db.execute(
            select(Bill)
            .where(
                Bill.organization_id == organization_id,
                Bill.supplier_id == supplier_id,
                Bill.status.in_([BillStatus.POSTED, BillStatus.PARTIALLY_PAID]),
            )
            .order_by(Bill.due_date.asc().nullslast(), Bill.bill_date.asc())
        )
        return list(result.scalars().all())
