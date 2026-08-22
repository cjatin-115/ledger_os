import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_dashboard_returns_organization_summary(client):
    response = await client.get("/api/v1/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert data["suppliers_count"] == 1
    assert data["bills_count"] == 0
    assert data["outstanding_amount"] == "0.00"


@pytest.mark.asyncio
async def test_readiness_returns_dependency_failure_without_redis(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.REDIS_URL", "redis://invalid-redis-host:6379/0")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/health/ready")

    assert response.status_code == 503
