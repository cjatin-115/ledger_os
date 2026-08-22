from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.account_transaction import AccountTransaction
from app.schemas.ledger import (
    LedgerTransactionResponse,
    ReconciliationResponse,
)


class LedgerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_transactions(
        self,
        organization_id: UUID,
        supplier_id: UUID | None = None,
    ) -> list[LedgerTransactionResponse]:
        statement = select(AccountTransaction).where(
            AccountTransaction.organization_id == organization_id,
        )
        if supplier_id is not None:
            statement = statement.where(
                AccountTransaction.supplier_id == supplier_id,
            )

        result = await self.db.execute(
            statement.order_by(
                AccountTransaction.transaction_date.desc(),
                AccountTransaction.created_at.desc(),
            )
        )
        return [LedgerTransactionResponse.model_validate(transaction) for transaction in result.scalars().all()]

    async def reconcile(
        self,
        organization_id: UUID,
    ) -> ReconciliationResponse:
        result = await self.db.execute(
            select(
                func.count(AccountTransaction.id),
                func.coalesce(
                    func.sum(AccountTransaction.debit_amount),
                    Decimal("0.00"),
                ),
                func.coalesce(
                    func.sum(AccountTransaction.credit_amount),
                    Decimal("0.00"),
                ),
            ).where(
                AccountTransaction.organization_id == organization_id,
            )
        )
        count, debits, credits = result.one()
        net_balance = Decimal(debits) - Decimal(credits)

        return ReconciliationResponse(
            transaction_count=count,
            total_debits=debits,
            total_credits=credits,
            net_balance=net_balance,
            balanced=net_balance >= 0,
        )
