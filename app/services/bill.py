from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.account_transaction import (
    AccountTransaction,
    AccountTransactionType,
)
from app.db.models.bill import Bill, BillSourceType, BillStatus
from app.db.models.bill_item import BillItem
from app.repositories.account_transaction import (
    AccountTransactionRepository,
)
from app.repositories.bill import BillRepository
from app.repositories.supplier import SupplierRepository
from app.schemas.bill import BillCreate


class BillService:
    """Business logic for supplier bills."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = BillRepository(db)
        self.supplier_repository = SupplierRepository(db)
        self.transaction_repository = AccountTransactionRepository(db)

    async def create(
        self,
        payload: BillCreate,
        organization_id: UUID,
    ) -> Bill:
        """Create a draft supplier bill."""

        supplier = await self.supplier_repository.get_by_id(
            supplier_id=payload.supplier_id,
            organization_id=organization_id,
        )

        if supplier is None:
            raise ValueError("Supplier not found.")

        bill_number = payload.bill_number.strip()

        if not bill_number:
            raise ValueError("Bill number cannot be blank.")

        existing_bill = await self.repository.get_by_number(
            supplier_id=payload.supplier_id,
            organization_id=organization_id,
            bill_number=bill_number,
        )

        if existing_bill is not None:
            raise ValueError(
                "A bill with this number already exists "
                "for this supplier."
            )

        if (
            payload.due_date is not None
            and payload.due_date < payload.bill_date
        ):
            raise ValueError(
                "Due date cannot be earlier than bill date."
            )

        if payload.discount_amount > payload.subtotal:
            raise ValueError(
                "Bill discount cannot exceed subtotal."
            )

        items: list[BillItem] = []

        for item_payload in payload.items:
            description = item_payload.description.strip()

            if not description:
                raise ValueError(
                    "Bill item description cannot be blank."
                )

            gross_amount = (
                item_payload.quantity
                * item_payload.unit_price
            )

            if item_payload.discount_amount > gross_amount:
                raise ValueError(
                    "Item discount cannot exceed gross item amount."
                )

            items.append(
                BillItem(
                    description=description,
                    quantity=item_payload.quantity,
                    unit=item_payload.unit.strip().upper(),
                    unit_price=item_payload.unit_price,
                    discount_amount=item_payload.discount_amount,
                    tax_rate=item_payload.tax_rate,
                    tax_amount=item_payload.tax_amount,
                    line_total=item_payload.line_total,
                    hsn_code=(
                        item_payload.hsn_code.strip()
                        if item_payload.hsn_code
                        else None
                    ),
                )
            )

        bill = Bill(
            organization_id=organization_id,
            supplier_id=supplier.id,
            bill_number=bill_number,
            bill_date=payload.bill_date,
            due_date=payload.due_date,
            subtotal=payload.subtotal,
            discount_amount=payload.discount_amount,
            taxable_amount=payload.taxable_amount,
            cgst_amount=payload.cgst_amount,
            sgst_amount=payload.sgst_amount,
            igst_amount=payload.igst_amount,
            total_amount=payload.total_amount,
            status=BillStatus.DRAFT,
            source_type=BillSourceType.MANUAL,
            notes=(
                payload.notes.strip()
                if payload.notes
                else None
            ),
            items=items,
        )

        try:
            bill = await self.repository.create(bill)
            await self.db.commit()
            return bill

        except Exception:
            await self.db.rollback()
            raise

    async def list(
        self,
        organization_id: UUID,
    ) -> list[Bill]:
        return await self.repository.list(
            organization_id=organization_id,
        )

    async def get(
        self,
        bill_id: UUID,
        organization_id: UUID,
    ) -> Bill | None:
        return await self.repository.get_by_id(
            bill_id=bill_id,
            organization_id=organization_id,
        )

    async def post(
        self,
        bill_id: UUID,
        organization_id: UUID,
    ) -> Bill:
        """Post a draft bill into the supplier ledger."""

        bill = await self.repository.get_by_id(
            bill_id=bill_id,
            organization_id=organization_id,
        )

        if bill is None:
            raise ValueError("Bill not found.")

        if bill.status != BillStatus.DRAFT:
            raise ValueError(
                f"Bill cannot be posted from status '{bill.status}'."
            )

        transaction = AccountTransaction(
            organization_id=organization_id,
            supplier_id=bill.supplier_id,
            transaction_type=AccountTransactionType.BILL,
            reference_type="bill",
            reference_id=bill.id,
            debit_amount=bill.total_amount,
            credit_amount=0,
            transaction_date=bill.bill_date,
            description=f"Supplier bill {bill.bill_number}",
        )

        try:
            await self.transaction_repository.create(transaction)

            bill.status = BillStatus.POSTED

            await self.db.flush()
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return bill