from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ledger import ReconciliationResponse
from app.services.ledger import LedgerService


class ReconciliationService:
    def __init__(self, db: AsyncSession) -> None:
        self.ledger_service = LedgerService(db)

    async def reconcile(
        self,
        organization_id: UUID,
    ) -> ReconciliationResponse:
        return await self.ledger_service.reconcile(organization_id)
