"""
Tests for Health, Readiness, CORS, and Global Error Handling.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root '/' endpoint returns expected app identity & URLs."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CloudForge API"
    assert data["version"] == "0.1.0"
    assert data["health"] == "/health"
    assert data["ready"] == "/ready"
    assert "docs" in data


@pytest.mark.asyncio
async def test_root_health_endpoint(client: AsyncClient):
    """Test root '/health' liveness probe."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert "environment" in data


@pytest.mark.asyncio
async def test_root_ready_endpoint(client: AsyncClient):
    """Test root '/ready' readiness probe with DB ping."""
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "environment" in data


@pytest.mark.asyncio
async def test_v1_health_and_ready_endpoints(client: AsyncClient):
    """Test versioned '/api/v1/health' and '/api/v1/ready'."""
    health_resp = await client.get("/api/v1/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"

    ready_resp = await client.get("/api/v1/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"
    assert ready_resp.json()["database"] == "connected"


@pytest.mark.asyncio
async def test_global_404_error_handler(client: AsyncClient):
    """Test that requesting a nonexistent route returns structured JSON error envelope."""
    response = await client.get("/nonexistent-endpoint-12345")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "HTTPException"
    assert "message" in data


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test that CORS headers are emitted for allowed frontend origin."""
    response = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
