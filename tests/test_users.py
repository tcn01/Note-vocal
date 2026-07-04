import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_user(client):
    await client.post(
        "/api/v1/users/",
        json={
            "email": "dupe@example.com",
            "password": "testpass123",
            "name": "Duplicate",
        },
    )
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "dupe@example.com",
            "password": "testpass123",
            "name": "Duplicate",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login(client):
    await client.post(
        "/api/v1/users/",
        json={
            "email": "login@example.com",
            "password": "testpass123",
            "name": "Login Test",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_read_current_user(client):
    await client.post(
        "/api/v1/users/",
        json={
            "email": "me@example.com",
            "password": "testpass123",
            "name": "Me",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "testpass123"},
    )
    token = login_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
