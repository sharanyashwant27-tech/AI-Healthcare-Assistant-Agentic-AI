import pytest


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_login_and_chat(client):
    login = await client.post(
        "/api/v1/login",
        json={"email": "patient@example.com", "password": "Patient@12345"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    chat = await client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "What does CDC say about chest pain emergencies?"},
    )
    assert chat.status_code == 200
    body = chat.json()
    assert "reply" in body
    assert "disclaimer" in body


@pytest.mark.asyncio
async def test_dashboard(client):
    login = await client.post(
        "/api/v1/login",
        json={"email": "admin@example.com", "password": "Admin@12345"},
    )
    token = login.json()["access_token"]
    dash = await client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash.status_code == 200
    assert "stats" in dash.json()
