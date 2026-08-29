import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_source_trust_history(async_client: AsyncClient):
    response = await async_client.get("/api/v1/sources/@dalalstreetinsider/trust-history")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["source_handle"] == "@dalalstreetinsider"
    assert data["total_claims_evaluated"] == 2
    assert data["accurate_claims_count"] == 2
    assert data["accuracy_rate"] == 1.0
    assert data["trust_score"] >= 0.70
    assert len(data["recent_trajectories"]) == 2


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    assert "qdrant" in data
