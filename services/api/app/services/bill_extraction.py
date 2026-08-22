from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.bill_extractor import extract_bill_from_image, extract_bill_from_text
from app.db.models.supplier import Supplier
from app.repositories.supplier import SupplierRepository
from app.schemas.bill import BillCreate, BillItemCreate
from app.schemas.bill_extraction import ExtractedBill


class BillExtractionService:
    """Convert raw OCR invoice text or image files into a normalized extracted bill schema."""

    def __init__(self, db: AsyncSession | None = None):
        self.db = db

    async def extract_from_text(self, raw_text: str) -> ExtractedBill:
        return extract_bill_from_text(raw_text)

    async def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> ExtractedBill:
        return extract_bill_from_image(image_bytes, mime_type)

    async def confirm_extracted_bill(
        self,
        payload: ExtractedBill,
        organization_id: UUID,
    ) -> dict:
        if self.db is None:
            raise ValueError("Database session is required to confirm extracted bills.")

        supplier_repo = SupplierRepository(self.db)

        supplier: Supplier | None = None
        created_supplier = False

        if payload.supplier_gstin:
            supplier = await supplier_repo.get_by_gstin(
                gstin=payload.supplier_gstin,
                organization_id=organization_id,
            )

        if supplier is None and payload.supplier_name:
            supplier = Supplier(
                organization_id=organization_id,
                name=payload.supplier_name.strip(),
                gstin=(payload.supplier_gstin.strip().upper() if payload.supplier_gstin else None),
                is_active=True,
            )
            supplier = await supplier_repo.create(supplier)
            created_supplier = True

        if supplier is None:
            raise ValueError("Supplier could not be resolved from the extracted invoice data.")

        items: list[BillItemCreate] = []
        for item in payload.items:
            items.append(
                BillItemCreate(
                    description=item.description or "Unspecified item",
                    quantity=item.quantity or Decimal("1"),
                    unit=item.unit or "PCS",
                    unit_price=item.unit_price or Decimal("0.00"),
                    discount_amount=item.discount_amount or Decimal("0.00"),
                    tax_rate=item.tax_rate or Decimal("0.00"),
                    tax_amount=item.tax_amount or Decimal("0.00"),
                    line_total=item.line_total or Decimal("0.00"),
                    hsn_code=item.hsn_code,
                )
            )

        subtotal = payload.subtotal or Decimal("0.00")
        discount_amount = payload.discount_amount or Decimal("0.00")
        taxable_amount = payload.taxable_amount or Decimal("0.00")
        cgst_amount = payload.cgst_amount or Decimal("0.00")
        sgst_amount = payload.sgst_amount or Decimal("0.00")
        igst_amount = payload.igst_amount or Decimal("0.00")
        total_amount = payload.total_amount or Decimal("0.00")

        # Auto-reconcile financial calculation fields to prevent validation errors
        if taxable_amount == Decimal("0.00"):
            if subtotal > Decimal("0.00"):
                taxable_amount = subtotal - discount_amount
            elif total_amount > Decimal("0.00"):
                taxable_amount = total_amount - (cgst_amount + sgst_amount + igst_amount)

        if total_amount == Decimal("0.00"):
            total_amount = taxable_amount + cgst_amount + sgst_amount + igst_amount

        # Guarantee expected_total equals total_amount
        expected_total = taxable_amount + cgst_amount + sgst_amount + igst_amount
        if total_amount != expected_total and total_amount > Decimal("0.00"):
            taxable_amount = total_amount - (cgst_amount + sgst_amount + igst_amount)

        # Guarantee subtotal matches taxable_amount + discount_amount
        subtotal = taxable_amount + discount_amount

        bill_payload = BillCreate(
            supplier_id=supplier.id,
            bill_number=(payload.bill_number or "AUTO-UNKNOWN").strip(),
            bill_date=payload.bill_date or __import__("datetime").date.today(),
            due_date=payload.due_date,
            subtotal=subtotal,
            discount_amount=discount_amount,
            taxable_amount=taxable_amount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
            total_amount=total_amount,
            notes="Created from OCR scan" if payload.warnings or True else None,
            items=items,
        )

        from app.services.bill import BillService

        bill_service = BillService(self.db)
        created_bill = await bill_service.create(
            payload=bill_payload,
            organization_id=organization_id,
        )

        return {
            "supplier_match": {
                "found": True,
                "created": created_supplier,
                "supplier_id": str(supplier.id),
                "name": supplier.name,
                "gstin": supplier.gstin,
            },
            "bill": created_bill,
        }
