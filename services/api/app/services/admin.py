from uuid import UUID

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.permission import Permission
from app.db.models.role import Role
from app.db.models.role_permission import RolePermission
from app.db.models.user import User
from app.schemas.admin import (
    RoleCreateRequest,
    RoleResponse,
    UserCreateRequest,
    UserResponse,
)


class OrganizationAdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_roles(self, organization_id: UUID) -> list[RoleResponse]:
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
            .where(Role.organization_id == organization_id)
            .order_by(Role.name)
        )
        return [self._role_response(role) for role in result.scalars().all()]

    async def create_role(
        self,
        organization_id: UUID,
        payload: RoleCreateRequest,
    ) -> RoleResponse:
        name = payload.name.strip()
        if not name:
            raise ValueError("Role name is required.")

        existing = await self.db.scalar(
            select(Role).where(
                Role.organization_id == organization_id,
                Role.name == name,
            )
        )
        if existing is not None:
            raise ValueError("A role with this name already exists.")

        role = Role(
            organization_id=organization_id,
            name=name,
            description=payload.description,
            is_active=True,
        )
        self.db.add(role)
        await self.db.flush()
        await self._assign_permissions(role, payload.permission_codes)
        await self.db.commit()
        await self.db.refresh(role)
        return await self._get_role_response(role.id, organization_id)

    async def list_users(self, organization_id: UUID) -> list[UserResponse]:
        result = await self.db.execute(
            select(User).where(User.organization_id == organization_id).order_by(User.full_name)
        )
        return [UserResponse.model_validate(user) for user in result.scalars()]

    async def create_user(
        self,
        organization_id: UUID,
        payload: UserCreateRequest,
    ) -> UserResponse:
        role = await self.db.scalar(
            select(Role).where(
                Role.id == payload.role_id,
                Role.organization_id == organization_id,
                Role.is_active.is_(True),
            )
        )
        if role is None:
            raise ValueError("Role not found in this organization.")

        email = payload.email.strip().lower()
        existing = await self.db.scalar(select(User).where(User.email == email))
        if existing is not None:
            raise ValueError("A user with this email already exists.")

        user = User(
            organization_id=organization_id,
            role_id=role.id,
            full_name=payload.full_name.strip(),
            email=email,
            phone_number=payload.phone_number.strip(),
            password_hash=bcrypt.hashpw(
                payload.password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8"),
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    async def _assign_permissions(
        self,
        role: Role,
        permission_codes: list[str],
    ) -> None:
        if not permission_codes:
            return
        result = await self.db.execute(select(Permission).where(Permission.code.in_(permission_codes)))
        permissions = list(result.scalars().all())
        if len(permissions) != len(set(permission_codes)):
            raise ValueError("One or more permissions do not exist.")
        self.db.add_all([RolePermission(role_id=role.id, permission_id=permission.id) for permission in permissions])

    async def _get_role_response(
        self,
        role_id: UUID,
        organization_id: UUID,
    ) -> RoleResponse:
        role = await self.db.scalar(
            select(Role)
            .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
            .where(
                Role.id == role_id,
                Role.organization_id == organization_id,
            )
        )
        if role is None:
            raise ValueError("Role not found.")
        return self._role_response(role)

    @staticmethod
    def _role_response(role: Role) -> RoleResponse:
        return RoleResponse(
            id=role.id,
            organization_id=role.organization_id,
            name=role.name,
            description=role.description,
            is_active=role.is_active,
            permission_codes=sorted(link.permission.code for link in role.role_permissions),
        )
