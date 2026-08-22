from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id, require_permission
from app.db.session import get_db
from app.schemas.payment import (
    PaymentAllocationCreate,
    PaymentAllocationResponse,
    PaymentCreate,
    PaymentResponse,
)
from app.services.payment import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_payment_service(
    db: AsyncSession = Depends(get_db),
) -> PaymentService:
    return PaymentService(db)


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payload: PaymentCreate,
    organization_id: UUID = Depends(get_current_organization_id),
    service: PaymentService = Depends(get_payment_service),
    _: object = Depends(require_permission("payments.write")),
) -> PaymentResponse:
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
    response_model=list[PaymentResponse],
)
async def list_payments(
    organization_id: UUID = Depends(get_current_organization_id),
    service: PaymentService = Depends(get_payment_service),
    _: object = Depends(require_permission("payments.read")),
) -> list[PaymentResponse]:
    return await service.list(
        organization_id=organization_id,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
async def get_payment(
    payment_id: UUID,
    organization_id: UUID = Depends(get_current_organization_id),
    service: PaymentService = Depends(get_payment_service),
    _: object = Depends(require_permission("payments.read")),
) -> PaymentResponse:
    payment = await service.get(
        payment_id=payment_id,
        organization_id=organization_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    return payment


@router.post(
    "/{payment_id}/allocate",
    response_model=PaymentAllocationResponse,
)
async def allocate_payment(
    payment_id: UUID,
    payload: PaymentAllocationCreate,
    organization_id: UUID = Depends(get_current_organization_id),
    service: PaymentService = Depends(get_payment_service),
    _: object = Depends(require_permission("payments.write")),
) -> PaymentAllocationResponse:
    try:
        return await service.allocate(
            payment_id=payment_id,
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
