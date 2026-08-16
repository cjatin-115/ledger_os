from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization import Organization
from app.db.models.role import Role
from app.db.models.user import User

DEVELOPMENT_ORGANIZATION_ID = UUID(
    "00000000-0000-0000-0000-000000000001"
)

DEVELOPMENT_USER_ID = UUID(
    "00000000-0000-0000-0000-000000000002"
)

DEVELOPMENT_ROLE_ID = UUID(
    "00000000-0000-0000-0000-000000000003"
)


async def seed_development_data(db: AsyncSession) -> None:
    """Create deterministic local development records."""

    organization = await db.get(
        Organization,
        DEVELOPMENT_ORGANIZATION_ID,
    )

    if organization is None:
        organization = Organization(
            id=DEVELOPMENT_ORGANIZATION_ID,
            name="LedgerOS Development Shop",
            gstin="27DEVSHOP0000Z5",
            is_active=True,
        )
        db.add(organization)

    role = await db.get(Role, DEVELOPMENT_ROLE_ID)

    if role is None:
        role = Role(
            id=DEVELOPMENT_ROLE_ID,
            organization_id=DEVELOPMENT_ORGANIZATION_ID,
            name="OWNER",
            description="Development owner role",
            is_active=True,
        )
        db.add(role)

    user = await db.get(User, DEVELOPMENT_USER_ID)

    if user is None:
        user = User(
            id=DEVELOPMENT_USER_ID,
            organization_id=DEVELOPMENT_ORGANIZATION_ID,
            role_id=DEVELOPMENT_ROLE_ID,
            phone_number="9999999999",
            full_name="Development User",
            email="dev@ledgeros.local",
            is_active=True,
        )
        db.add(user)

    await db.commit()