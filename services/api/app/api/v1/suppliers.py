from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id, require_permission
from app.db.session import get_db
from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)
from app.services.supplier import SupplierService

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


def get_supplier_service(
    db: AsyncSession = Depends(get_db),
) -> SupplierService:
    return SupplierService(db)


@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    payload: SupplierCreate,
    organization_id: UUID = Depends(get_current_organization_id),
    service: SupplierService = Depends(get_supplier_service),
    _: object = Depends(require_permission("suppliers.write")),
) -> SupplierResponse:
    try:
        return await service.create(
            payload=payload,
            organization_id=organization_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[SupplierResponse],
)
async def list_suppliers(
    organization_id: UUID = Depends(get_current_organization_id),
    service: SupplierService = Depends(get_supplier_service),
    _: object = Depends(require_permission("suppliers.read")),
) -> list[SupplierResponse]:
    return await service.list(
        organization_id=organization_id,
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
)
async def get_supplier(
    supplier_id: UUID,
    organization_id: UUID = Depends(get_current_organization_id),
    service: SupplierService = Depends(get_supplier_service),
    _: object = Depends(require_permission("suppliers.read")),
) -> SupplierResponse:
    supplier = await service.get(
        supplier_id=supplier_id,
        organization_id=organization_id,
    )

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    return supplier


@router.patch(
    "/{supplier_id}",
    response_model=SupplierResponse,
)
async def update_supplier(
    supplier_id: UUID,
    payload: SupplierUpdate,
    organization_id: UUID = Depends(get_current_organization_id),
    service: SupplierService = Depends(get_supplier_service),
    _: object = Depends(require_permission("suppliers.write")),
) -> SupplierResponse:
    try:
        supplier = await service.update(
            supplier_id=supplier_id,
            payload=payload,
            organization_id=organization_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    return supplier