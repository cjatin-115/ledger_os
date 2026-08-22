from collections.abc import AsyncGenerator
from uuid import UUID

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.api.deps import get_current_organization_id, get_current_user
from app.core.config import settings
from app.core.permissions import PERMISSION_CATALOG
from app.db.models.account_transaction import AccountTransaction
from app.db.models.bill import Bill
from app.db.models.organization import Organization
from app.db.models.payment import Payment
from app.db.models.payment_allocation import PaymentAllocation
from app.db.models.permission import Permission
from app.db.models.role import Role
from app.db.models.role_permission import RolePermission
from app.db.models.supplier import Supplier
from app.db.models.user import User
from app.db.session import get_db
from app.main import app

TEST_ORGANIZATION_ID = UUID(
    "00000000-0000-0000-0000-000000000010"
)

TEST_SUPPLIER_ID = UUID(
    "00000000-0000-0000-0000-000000000011"
)

TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000012")
TEST_ROLE_ID = UUID("00000000-0000-0000-0000-000000000013")


test_engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def override_get_current_organization_id() -> UUID:
    return TEST_ORGANIZATION_ID


async def override_get_current_user() -> User:
    async with TestSessionLocal() as db:
        user = await db.get(User, TEST_USER_ID)
        if user is None:
            raise RuntimeError("Test user was not seeded.")
        return user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[
    get_current_organization_id
] = override_get_current_organization_id
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with TestSessionLocal() as db:
        organization = await db.get(
            Organization,
            TEST_ORGANIZATION_ID,
        )

        if organization is None:
            organization = Organization(
                id=TEST_ORGANIZATION_ID,
                name="LedgerOS Test Organization",
                gstin=None,
                is_active=True,
            )
            db.add(organization)

        role = await db.get(Role, TEST_ROLE_ID)
        if role is None:
            role = Role(
                id=TEST_ROLE_ID,
                organization_id=TEST_ORGANIZATION_ID,
                name="TEST_OWNER",
                description="Test owner role",
                is_active=True,
            )
            db.add(role)
            await db.flush()

        permission_result = await db.execute(
            select(Permission).where(
                Permission.code.in_(PERMISSION_CATALOG.keys())
            )
        )
        permissions = {
            permission.code: permission
            for permission in permission_result.scalars().all()
        }
        for code, (description, category) in PERMISSION_CATALOG.items():
            permission = permissions.get(code)
            if permission is None:
                permission = Permission(
                    code=code,
                    description=description,
                    category=category,
                )
                db.add(permission)
                await db.flush()
                permissions[code] = permission
            existing_link = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == TEST_ROLE_ID,
                    RolePermission.permission_id == permission.id,
                )
            )
            if existing_link.scalar_one_or_none() is None:
                db.add(
                    RolePermission(
                        role_id=TEST_ROLE_ID,
                        permission_id=permission.id,
                    )
                )

        test_user = await db.get(User, TEST_USER_ID)
        if test_user is None:
            db.add(
                User(
                    id=TEST_USER_ID,
                    organization_id=TEST_ORGANIZATION_ID,
                    role_id=TEST_ROLE_ID,
                    phone_number="9999999998",
                    full_name="Test Owner",
                    email="test-owner@ledgeros.local",
                    password_hash="",
                    is_active=True,
                )
            )

        supplier = await db.get(
            Supplier,
            TEST_SUPPLIER_ID,
        )

        if supplier is None:
            supplier = Supplier(
                id=TEST_SUPPLIER_ID,
                organization_id=TEST_ORGANIZATION_ID,
                name="Test Supplier",
                contact_person="Test Contact",
                phone="9999999999",
                email="test@supplier.local",
                gstin="27TESTSUPPLR01",
                address="Test Address",
                payment_terms_days=30,
                is_active=True,
            )
            db.add(supplier)

        await db.commit()

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    async with TestSessionLocal() as db:
        await db.execute(
            delete(PaymentAllocation).where(
                PaymentAllocation.payment_id.in_(
                    select(Payment.id).where(
                        Payment.organization_id == TEST_ORGANIZATION_ID
                    )
                )
            )
        )

        await db.execute(
            delete(AccountTransaction).where(
                AccountTransaction.organization_id
                == TEST_ORGANIZATION_ID
            )
        )

        await db.execute(
            delete(Payment).where(
                Payment.organization_id == TEST_ORGANIZATION_ID
            )
        )

        await db.execute(
            delete(Bill).where(
                Bill.organization_id == TEST_ORGANIZATION_ID
            )
        )

        await db.execute(
            delete(Supplier).where(
                Supplier.organization_id == TEST_ORGANIZATION_ID
            )
        )

        await db.commit()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_test_engine() -> AsyncGenerator[None, None]:
    yield
    await test_engine.dispose()