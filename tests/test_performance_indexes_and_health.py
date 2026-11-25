"""
TRUSTLENS AI - FastAPI & MongoDB Optimization Verification Tests
Verifies X-Request-ID / X-Correlation-ID / X-Process-Time headers,
live /api/v1/health db_ping_ms diagnostics, and IXSCAN index usage.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager


@pytest.fixture(autouse=True)
async def setup_db():
    await db_manager.connect()
    yield
    await db_manager.disconnect()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_ping_and_request_id_headers(client: AsyncClient):
    res = await client.get("/api/v1/health", headers={"X-Request-ID": "req-bench-123"})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == "req-bench-123"
    assert res.headers.get("X-Correlation-ID") == "req-bench-123"
    assert res.headers.get("X-Process-Time", "").endswith("ms")

    body = res.json()
    assert body["database_connected"] is True
    assert isinstance(body["db_ping_ms"], float)
    assert body["status"] == "healthy"


@pytest.mark.asyncio
async def test_mongodb_owner_id_uses_index_scan():
    exp = await db_manager.db.command(
        "explain",
        {"find": "investigations", "filter": {"owner_id": "a22d3504-399f-4b0c-ac20-1a334aa1da22"}},
    )
    plan = exp.get("queryPlanner", {}).get("winningPlan", {})
    assert "IXSCAN" in str(plan), f"Expected IXSCAN, got {plan}"
