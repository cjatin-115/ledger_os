from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id
from app.db.session import get_db
from app.schemas.bill import BillCreate, BillResponse
from app.services.bill import BillService

router = APIRouter(
    prefix="/bills",
    tags=["Bills"],
)


def get_bill_service(
    db: AsyncSession = Depends(get_db),
) -> BillService:
    return BillService(db)


@router.post(
    "",
    response_model=BillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_bill(
    payload: BillCreate,
    organization_id: UUID = Depends(get_current_organization_id),
    service: BillService = Depends(get_bill_service),
) -> BillResponse:
    try:
        return await service.create(
            payload=payload,
            organization_id=organization_id,
        )
    except ValueError as exc:
        message = str(exc)

        if "not found" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        ) from exc


@router.get(
    "",
    response_model=list[BillResponse],
)
async def list_bills(
    organization_id: UUID = Depends(get_current_organization_id),
    service: BillService = Depends(get_bill_service),
) -> list[BillResponse]:
    return await service.list(
        organization_id=organization_id,
    )


@router.get(
    "/{bill_id}",
    response_model=BillResponse,
)
async def get_bill(
    bill_id: UUID,
    organization_id: UUID = Depends(get_current_organization_id),
    service: BillService = Depends(get_bill_service),
) -> BillResponse:
    bill = await service.get(
        bill_id=bill_id,
        organization_id=organization_id,
    )

    if bill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found.",
        )

    return bill

@router.post(
    "/{bill_id}/post",
    response_model=BillResponse,
)
async def post_bill(
    bill_id: UUID,
    organization_id: UUID = Depends(get_current_organization_id),
    service: BillService = Depends(get_bill_service),
) -> BillResponse:
    try:
        return await service.post(
            bill_id=bill_id,
            organization_id=organization_id,
        )
    except ValueError as exc:
        message = str(exc)

        if "not found" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        ) from exc