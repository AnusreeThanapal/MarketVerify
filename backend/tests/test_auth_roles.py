import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import create_app
from backend.scripts.seed_demo_users import seed_demo_users_and_claims


@pytest.fixture(autouse=True)
async def ensure_demo_users():
    await seed_demo_users_and_claims()


@pytest.mark.asyncio
async def test_login_success_and_jwt_claims():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            json={
                "email": "analyst.demo@marketverify.app",
                "password": "Analyst@Demo123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "analyst.demo@marketverify.app"
        assert data["user"]["role"] == "ANALYST"


@pytest.mark.asyncio
async def test_login_failure_invalid_password():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            json={
                "email": "analyst.demo@marketverify.app",
                "password": "WrongPassword999",
            },
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_me():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login
        login_res = await ac.post(
            "/api/v1/auth/login",
            json={
                "email": "compliance.demo@marketverify.app",
                "password": "Compliance@Demo123",
            },
        )
        token = login_res.json()["access_token"]

        # 2. Query /me
        me_res = await ac.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        user_data = me_res.json()
        assert user_data["email"] == "compliance.demo@marketverify.app"
        assert user_data["role"] == "COMPLIANCE_OFFICER"


@pytest.mark.asyncio
async def test_role_guarded_admin_data_access():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # A. Login Analyst
        analyst_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "analyst.demo@marketverify.app", "password": "Analyst@Demo123"},
        )
        analyst_token = analyst_login.json()["access_token"]

        # B. Login Compliance Officer
        compliance_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "compliance.demo@marketverify.app", "password": "Compliance@Demo123"},
        )
        compliance_token = compliance_login.json()["access_token"]

        # C. Login Administrator
        admin_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "admin.demo@marketverify.app", "password": "Admin@Demo123"},
        )
        admin_token = admin_login.json()["access_token"]

        # D. Login Auditor
        auditor_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "auditor.demo@marketverify.app", "password": "Auditor@Demo123"},
        )
        auditor_token = auditor_login.json()["access_token"]

        # Assert Analyst gets 403 on /admin/data/users
        res = await ac.get("/api/v1/admin/data/users", headers={"Authorization": f"Bearer {analyst_token}"})
        assert res.status_code == 403

        # Assert Compliance gets 403 on /admin/data/claims
        res = await ac.get("/api/v1/admin/data/claims", headers={"Authorization": f"Bearer {compliance_token}"})
        assert res.status_code == 403

        # Assert Admin gets 200 on /admin/data/users
        res = await ac.get("/api/v1/admin/data/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        assert "items" in res.json()

        # Assert Auditor gets 200 on /admin/data/claims
        res = await ac.get("/api/v1/admin/data/claims", headers={"Authorization": f"Bearer {auditor_token}"})
        assert res.status_code == 200
        assert "items" in res.json()


@pytest.mark.asyncio
async def test_users_endpoint_never_exposes_password_hash():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        admin_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "admin.demo@marketverify.app", "password": "Admin@Demo123"},
        )
        admin_token = admin_login.json()["access_token"]

        res = await ac.get("/api/v1/admin/data/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        users_list = res.json()["items"]
        assert len(users_list) >= 4
        for u in users_list:
            assert "hashed_password" not in u
            assert "password" not in u


@pytest.mark.asyncio
async def test_admin_data_claims_and_qdrant_endpoints():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        admin_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "admin.demo@marketverify.app", "password": "Admin@Demo123"},
        )
        admin_token = admin_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Test claims with pagination and search
        claims_res = await ac.get("/api/v1/admin/data/claims?limit=5", headers=headers)
        assert claims_res.status_code == 200
        data = claims_res.json()
        assert data["limit"] == 5
        assert "items" in data

        # Test trust-tier docs endpoint
        trust_res = await ac.get("/api/v1/admin/data/trust-tier-docs", headers=headers)
        assert trust_res.status_code == 200
        assert "collection" in trust_res.json()

        # Test filing docs endpoint
        filing_res = await ac.get("/api/v1/admin/data/filing-docs", headers=headers)
        assert filing_res.status_code == 200

        # Test sentiment docs endpoint
        sentiment_res = await ac.get("/api/v1/admin/data/sentiment-docs", headers=headers)
        assert sentiment_res.status_code == 200
