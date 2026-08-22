from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.account_transaction import AccountTransaction


class AccountTransactionRepository:
    """Database operations for supplier ledger transactions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        transaction: AccountTransaction,
    ) -> AccountTransaction:
        """Persist a ledger transaction."""

        self.db.add(transaction)
        await self.db.flush()

        return transaction
