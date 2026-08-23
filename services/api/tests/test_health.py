import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_head_and_get_health_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # /health endpoint (used by UptimeRobot & Render health checks)
        res_head = await ac.head("/health")
        assert res_head.status_code == 200
        assert res_head.content == b""

        res_get = await ac.get("/health")
        assert res_get.status_code == 200
        assert res_get.json() == {"status": "healthy"}

        # root / endpoint
        root_head = await ac.head("/")
        assert root_head.status_code == 200
        assert root_head.content == b""

        root_get = await ac.get("/")
        assert root_get.status_code == 200

        # /api/v1/health endpoint
        api_head = await ac.head("/api/v1/health")
        assert api_head.status_code == 200
        assert api_head.content == b""



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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health/ready")

    assert response.status_code == 503
