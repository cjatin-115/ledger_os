from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id, require_permission
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("", response_model=DashboardSummaryResponse)
async def get_dashboard(
    organization_id: UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("dashboard.read")),
) -> DashboardSummaryResponse:
    return await DashboardService(db).summary(organization_id)