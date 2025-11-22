"""
Tests for authentication flows - register, login, refresh, me
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import User
from copy_that.infrastructure.security.authentication import get_password_hash


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        roles='["user"]',
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestRegistration:
    """Test user registration"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with existing email fails"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "AnotherPass123!",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "short",  # Too short
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "ValidPass123!",
            },
        )

        assert response.status_code == 422


class TestLogin:
    """Test user login"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login returns tokens"""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPassword123!"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password fails"""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "WrongPassword123!"},
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails"""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "nobody@example.com", "password": "SomePassword123!"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_disabled_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test login with disabled account fails"""
        # Create disabled user
        user = User(
            email="disabled@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=False,
            roles='["user"]',
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "disabled@example.com", "password": "TestPassword123!"},
        )

        assert response.status_code == 403
        assert "disabled" in response.json()["detail"]


class TestTokenRefresh:
    """Test token refresh"""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient, test_user):
        """Test successful token refresh"""
        # First login to get tokens
        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        # Refresh tokens
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, client: AsyncClient, test_user):
        """Test refresh with access token (not refresh token) fails"""
        # Login to get tokens
        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        # Try to refresh with access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["access_token"]},  # Wrong token type
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token fails"""
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == 401


class TestCurrentUser:
    """Test /me endpoint"""

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, test_user):
        """Test getting current user info"""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        # Get current user
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_current_user_no_auth(self, client: AsyncClient):
        """Test /me without auth fails"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test /me with invalid token fails"""
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401
