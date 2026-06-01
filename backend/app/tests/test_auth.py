import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from fastapi import status
from datetime import datetime, timedelta, timezone

from app.main import app
from app.core.database import get_db
from app.core.exceptions import (
    AuthenticationError, ValidationError, ConflictError,
    NotFoundError, BusinessLogicError
)
from app.models.user import UserRole

pytestmark = pytest.mark.asyncio


class TestRegister:
    @patch("app.api.v1.auth.EmailService.send_verification_email", new_callable=AsyncMock)
    async def test_register_success(self, mock_send_email: AsyncMock, async_client: AsyncClient, test_category, test_priority):
        payload = {
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "New",
            "last_name": "User",
            "agree_terms": True,
            "privacy_policy": True,
            "phone_number": "+21698765432",
        }
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data.get("data", {})

    async def test_register_duplicate_email(self, async_client: AsyncClient, test_user):
        payload = {
            "email": "citizen@test.com",
            "username": "another_user",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "New",
            "last_name": "User",
            "agree_terms": True,
            "privacy_policy": True,
        }
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_register_weak_password(self, async_client: AsyncClient):
        payload = {
            "email": "weak@test.com",
            "username": "weakuser",
            "password": "short",
            "confirm_password": "short",
            "first_name": "Weak",
            "last_name": "User",
            "agree_terms": True,
            "privacy_policy": True,
        }
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    async def test_login_success(self, async_client: AsyncClient, test_user):
        payload = {
            "email": "citizen@test.com",
            "password": "TestPass123!",
        }
        response = await async_client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data.get("data", {})

    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        payload = {
            "email": "wrong@test.com",
            "password": "WrongPass123!",
        }
        response = await async_client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_unverified_email(self, async_client: AsyncClient, unverified_user):
        payload = {
            "email": "unverified@test.com",
            "password": "TestPass123!",
        }
        response = await async_client.post("/api/v1/auth/login", json=payload)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


class TestRefreshToken:
    async def test_refresh_token(self, async_client: AsyncClient, refresh_token_str: str):
        response = await async_client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": refresh_token_str}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data.get("data", {})

    async def test_refresh_token_expired(self, async_client: AsyncClient):
        from jose import jwt
        from app.core.config import settings
        expired = jwt.encode(
            {"sub": "1", "role": "citizen", "exp": datetime.now(timezone.utc) - timedelta(hours=1), "type": "refresh"},
            settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        response = await async_client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": expired}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUser:
    async def test_get_current_user(self, async_client: AsyncClient, auth_headers: dict, test_user):
        response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

    async def test_get_current_user_no_auth(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


class TestChangePassword:
    async def test_change_password(self, async_client: AsyncClient, auth_headers: dict):
        payload = {
            "current_password": "TestPass123!",
            "new_password": "NewPass456!",
            "confirm_new_password": "NewPass456!",
        }
        response = await async_client.put(
            "/api/v1/auth/me/password",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_change_password_wrong_current(self, async_client: AsyncClient, auth_headers: dict):
        payload = {
            "current_password": "WrongPass123!",
            "new_password": "NewPass456!",
            "confirm_new_password": "NewPass456!",
        }
        response = await async_client.put(
            "/api/v1/auth/me/password",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
