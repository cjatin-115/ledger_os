from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.device_session import DeviceSession
from app.db.models.permission import Permission
from app.db.models.role_permission import RolePermission
from app.db.models.user import User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")
    organization_id = payload.get("org_id")

    if not user_id or not organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User).where(
            User.id == UUID(user_id),
            User.organization_id == UUID(organization_id),
            User.is_active.is_(True),
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active or no longer valid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_id = payload.get("sid")
    if session_id:
        session = await db.get(DeviceSession, UUID(session_id))
        if session is None or session.user_id != user.id or not session.is_active or session.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Device session is no longer active.",
            )

    return user


def require_permission(permission_code: str):
    async def _require_permission(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        permission_result = await db.execute(
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id == user.role_id,
                Permission.code == permission_code,
            )
        )

        if permission_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission_code}",
            )

        return user

    return _require_permission


async def get_current_organization_id(
    user: User = Depends(get_current_user),
) -> UUID:
    return user.organization_id


async def get_current_user_id(
    user: User = Depends(get_current_user),
) -> UUID:
    return user.id
