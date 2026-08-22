from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id, require_permission
from app.db.session import get_db
from app.schemas.admin import (
    RoleCreateRequest,
    RoleResponse,
    UserCreateRequest,
    UserResponse,
)
from app.services.admin import OrganizationAdminService

router = APIRouter(prefix="/admin", tags=["Administration"])


def get_admin_service(
    db: AsyncSession = Depends(get_db),
) -> OrganizationAdminService:
    return OrganizationAdminService(db)


@router.get(
    "/roles",
    response_model=list[RoleResponse],
)
async def list_roles(
    organization_id: UUID = Depends(get_current_organization_id),
    service: OrganizationAdminService = Depends(get_admin_service),
    _: object = Depends(require_permission("roles.manage")),
) -> list[RoleResponse]:
    return await service.list_roles(organization_id)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    payload: RoleCreateRequest,
    organization_id: UUID = Depends(get_current_organization_id),
    service: OrganizationAdminService = Depends(get_admin_service),
    _: object = Depends(require_permission("roles.manage")),
) -> RoleResponse:
    try:
        return await service.create_role(organization_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    organization_id: UUID = Depends(get_current_organization_id),
    service: OrganizationAdminService = Depends(get_admin_service),
    _: object = Depends(require_permission("users.manage")),
) -> list[UserResponse]:
    return await service.list_users(organization_id)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreateRequest,
    organization_id: UUID = Depends(get_current_organization_id),
    service: OrganizationAdminService = Depends(get_admin_service),
    _: object = Depends(require_permission("users.manage")),
) -> UserResponse:
    try:
        return await service.create_user(organization_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc