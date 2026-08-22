from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.account_transaction import (
    AccountTransaction,
    AccountTransactionType,
)
from app.db.models.bill import BillStatus
from app.db.models.payment import Payment, PaymentMethod, PaymentStatus
from app.db.models.payment_allocation import PaymentAllocation
from app.repositories.account_transaction import (
    AccountTransactionRepository,
)
from app.repositories.bill import BillRepository
from app.repositories.payment import PaymentRepository
from app.repositories.payment_allocation import (
    PaymentAllocationRepository,
)
from app.repositories.supplier import SupplierRepository
from app.schemas.payment import (
    PaymentAllocationCreate,
    PaymentCreate,
)


class PaymentService:
    """Business logic for supplier payments and allocations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

        self.repository = PaymentRepository(db)
        self.allocation_repository = PaymentAllocationRepository(db)
        self.bill_repository = BillRepository(db)
        self.supplier_repository = SupplierRepository(db)
        self.transaction_repository = AccountTransactionRepository(db)

    async def create(
        self,
        payload: PaymentCreate,
        organization_id: UUID,
    ) -> Payment:
        """Record a new supplier payment."""

        supplier = await self.supplier_repository.get_by_id(
            supplier_id=payload.supplier_id,
            organization_id=organization_id,
        )

        if supplier is None:
            raise ValueError("Supplier not found.")

        payment_method = payload.payment_method.strip().lower()

        try:
            payment_method_enum = PaymentMethod(payment_method)
        except ValueError as exc:
            raise ValueError(
                f"Invalid payment method: {payment_method}."
            ) from exc

        payment = Payment(
            organization_id=organization_id,
            supplier_id=supplier.id,
            amount=payload.amount,
            payment_method=payment_method_enum,
            payment_date=payload.payment_date,
            reference_number=(
                payload.reference_number.strip()
                if payload.reference_number
                else None
            ),
            cheque_number=(
                payload.cheque_number.strip()
                if payload.cheque_number
                else None
            ),
            cheque_date=payload.cheque_date,
            bank_name=(
                payload.bank_name.strip()
                if payload.bank_name
                else None
            ),
            status=PaymentStatus.RECORDED,
            notes=(
                payload.notes.strip()
                if payload.notes
                else None
            ),
        )

        try:
            payment = await self.repository.create(payment)
            await self.db.commit()
            return payment

        except Exception:
            await self.db.rollback()
            raise

    async def list(
        self,
        organization_id: UUID,
    ) -> list[Payment]:
        return await self.repository.list(
            organization_id=organization_id,
        )

    async def get(
        self,
        payment_id: UUID,
        organization_id: UUID,
    ) -> Payment | None:
        return await self.repository.get_by_id(
            payment_id=payment_id,
            organization_id=organization_id,
        )

    async def allocate(
        self,
        payment_id: UUID,
        payload: PaymentAllocationCreate,
        organization_id: UUID,
    ) -> PaymentAllocation:
        """Allocate part of a payment to a supplier bill."""

        payment = await self.repository.get_by_id(
            payment_id=payment_id,
            organization_id=organization_id,
            for_update=True,
        )

        if payment is None:
            raise ValueError("Payment not found.")

        if payment.status != PaymentStatus.RECORDED:
            raise ValueError(
                "Only recorded payments can be allocated."
            )

        bill = await self.bill_repository.get_by_id(
            bill_id=payload.bill_id,
            organization_id=organization_id,
            for_update=True,
        )

        if bill is None:
            raise ValueError("Bill not found.")

        if bill.supplier_id != payment.supplier_id:
            raise ValueError(
                "Payment and bill must belong to the same supplier."
            )

        if bill.status in {
            BillStatus.CANCELLED,
            BillStatus.DRAFT,
        }:
            raise ValueError(
                "Only posted bills can receive payments."
            )

        allocated_to_payment = (
            await self.allocation_repository.get_total_allocated(
                payment_id=payment.id,
            )
        )

        payment_remaining = (
            Decimal(payment.amount) - Decimal(allocated_to_payment)
        )

        if payload.amount > payment_remaining:
            raise ValueError(
                "Allocation exceeds the remaining payment amount."
            )

        allocated_to_bill = (
            await self.allocation_repository.get_total_allocated_to_bill(
                bill_id=bill.id,
            )
        )

        bill_outstanding = (
            Decimal(bill.total_amount)
            - Decimal(allocated_to_bill)
        )

        if payload.amount > bill_outstanding:
            raise ValueError(
                "Allocation exceeds the bill outstanding amount."
            )

        allocation = PaymentAllocation(
            payment_id=payment.id,
            bill_id=bill.id,
            amount=payload.amount,
        )

        try:
            allocation = await self.allocation_repository.create(
                allocation
            )

            transaction = AccountTransaction(
                organization_id=organization_id,
                supplier_id=payment.supplier_id,
                transaction_type=AccountTransactionType.PAYMENT,
                reference_type="payment",
                reference_id=payment.id,
                debit_amount=0,
                credit_amount=payload.amount,
                transaction_date=payment.payment_date,
                description=(
                    f"Payment allocated to bill "
                    f"{bill.bill_number}"
                ),
            )

            await self.transaction_repository.create(transaction)

            new_bill_outstanding = (
                bill_outstanding - payload.amount
            )

            if new_bill_outstanding == 0:
                bill.status = BillStatus.PAID
            else:
                bill.status = BillStatus.PARTIALLY_PAID

            await self.db.flush()
            await self.db.commit()

            return allocation

        except Exception:
            await self.db.rollback()
            raise