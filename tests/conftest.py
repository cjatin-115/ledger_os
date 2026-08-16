from collections.abc import AsyncGenerator
from uuid import UUID

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.api.deps import get_current_organization_id
from app.core.config import settings
from app.db.models.organization import Organization
from app.db.models.supplier import Supplier
from app.db.session import get_db
from app.main import app

TEST_ORGANIZATION_ID = UUID(
    "00000000-0000-0000-0000-000000000010"
)


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


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[
    get_current_organization_id
] = override_get_current_organization_id


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
            await db.commit()

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    async with TestSessionLocal() as db:
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