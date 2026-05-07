

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient) -> None:
    """New email + valid password → 201, body contains access_token."""
    response = await client.post(
        "/auth/signup",
        json={"email": "newuser@example.com", "password": "validpass123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient) -> None:
    """Signing up twice with the same email → 400 on the second attempt."""
    payload = {"email": "duplicate@example.com", "password": "validpass123"}

    first = await client.post("/auth/signup", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/signup", json=payload)
    assert second.status_code == 400
    assert "already exists" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_password_too_short(client: AsyncClient) -> None:
    """Password under 8 chars → 422 Unprocessable Entity from Pydantic."""
    response = await client.post(
        "/auth/signup",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient) -> None:
    """Malformed email address → 422 from Pydantic EmailStr validation."""
    response = await client.post(
        "/auth/signup",
        json={"email": "not-an-email", "password": "validpass123"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict) -> None:
    """Correct credentials → 200, body contains access_token."""
    response = await client.post(
        "/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: dict) -> None:
    """Correct email but wrong password → 401."""
    response = await client.post(
        "/auth/login",
        json={"email": test_user["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """Login with an email that was never registered → 401."""
    response = await client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "doesntmatter"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_no_token(client: AsyncClient) -> None:
    """GET /matches without Authorization header → 401."""
    response = await client.get("/matches")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_invalid_token(client: AsyncClient) -> None:
    """GET /matches with a malformed JWT → 401."""
    response = await client.get(
        "/matches",
        headers={"Authorization": "Bearer this.is.not.a.real.jwt"},
    )
    assert response.status_code == 401