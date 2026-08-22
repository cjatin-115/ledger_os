from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id, require_permission
from app.db.session import get_db
from app.schemas.ledger import (
    LedgerTransactionResponse,
    ReconciliationResponse,
)
from app.services.ledger import LedgerService
from app.services.reconciliation import ReconciliationService

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("", response_model=list[LedgerTransactionResponse])
async def list_ledger_transactions(
    supplier_id: UUID | None = None,
    organization_id: UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("ledger.read")),
) -> list[LedgerTransactionResponse]:
    return await LedgerService(db).list_transactions(
        organization_id=organization_id,
        supplier_id=supplier_id,
    )


@router.get(
    "/reconciliation",
    response_model=ReconciliationResponse,
)
async def reconcile_ledger(
    organization_id: UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("ledger.reconcile")),
) -> ReconciliationResponse:
    return await ReconciliationService(db).reconcile(organization_id)
