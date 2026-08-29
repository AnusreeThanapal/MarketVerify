import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_post_and_get_claim_flow(async_client: AsyncClient):
    # 1. Submit a claim
    payload = {
        "raw_text": "Reliance Retail is in talks to acquire 40% stake in quick commerce app Zepto.",
        "source_handle": "@dalalstreetinsider",
        "ticker": "RELIANCE",
    }
    response = await async_client.post("/api/v1/claims", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert data["status"] == "COMPLETED"
    assert data["ticker"] == "RELIANCE"
    assert data["verdict"] is not None
    assert "confidence_score" in data["verdict"]
    assert "citations" in data["verdict"]
    assert len(data["trace"]) >= 5

    claim_id = data["id"]

    # 2. Get claim by ID
    get_res = await async_client.get(f"/api/v1/claims/{claim_id}")
    assert get_res.status_code == 200
    claim_data = get_res.json()
    assert claim_data["id"] == claim_id
    assert claim_data["source_handle"] == "@dalalstreetinsider"
    assert len(claim_data["trace"]) >= 5

    # 3. List claims
    list_res = await async_client.get("/api/v1/claims?page=1&page_size=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert len(list_data["items"]) >= 1


@pytest.mark.asyncio
async def test_post_tamil_claim(async_client: AsyncClient):
    payload = {
        "raw_text": "டாடா ஸ்டீல் 1:10 பங்கு பிரிப்பு அறிவிக்க உள்ளதாக தகவல்",
        "source_handle": "@tamil_market_guru",
    }
    response = await async_client.post("/api/v1/claims", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["language"] == "ta"
    assert data["ticker"] == "TATASTEEL"
    assert data["verdict"] is not None
