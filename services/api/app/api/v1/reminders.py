from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id, require_permission
from app.db.session import get_db
from app.schemas.reminder import DueReminderResponse
from app.services.reminder import ReminderService

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("/due", response_model=list[DueReminderResponse])
async def due_reminders(
    days: int = Query(default=7, ge=0, le=365),
    organization_id: UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("bills.read")),
) -> list[DueReminderResponse]:
    return await ReminderService(db).due_bills(organization_id, days)
