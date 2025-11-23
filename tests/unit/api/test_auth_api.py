"""Comprehensive tests for auth API endpoints to achieve 80%+ coverage"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.domain.models import User
from copy_that.infrastructure.database import Base, get_db
from copy_that.infrastructure.security.authentication import get_password_hash
from copy_that.interfaces.api.main import app


@pytest_asyncio.fixture
async def async_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(async_db):
    """Create a test client with mocked database"""

    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(async_db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        roles='["user"]',
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(async_db):
    """Create an admin user with multiple roles"""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Admin User",
        roles='["user", "admin"]',
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


class TestRegistration:
    """Test user registration endpoint"""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
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
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_register_without_full_name(self, client):
        """Test registration without optional full_name"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "minimal@example.com",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "minimal@example.com"
        assert data["full_name"] is None

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
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
    async def test_register_short_password(self, client):
        """Test registration with password shorter than 8 chars"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email_format(self, client):
        """Test registration with invalid email format"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "ValidPass123!",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_email(self, client):
        """Test registration without email fails"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "password": "ValidPass123!",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_password(self, client):
        """Test registration without password fails"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "nopass@example.com",
            },
        )

        assert response.status_code == 422


class TestLogin:
    """Test login/token endpoint"""

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """Test successful login returns token pair"""
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
    async def test_login_admin_user(self, client, admin_user):
        """Test login with admin user (multiple roles)"""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "admin@example.com", "password": "AdminPass123!"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails"""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "WrongPassword123!"},
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails"""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "nobody@example.com", "password": "SomePassword123!"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_disabled_user(self, client, async_db):
        """Test login with disabled account fails"""
        user = User(
            email="disabled@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=False,
            roles='["user"]',
        )
        async_db.add(user)
        await async_db.commit()

        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "disabled@example.com", "password": "TestPassword123!"},
        )

        assert response.status_code == 403
        assert "disabled" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_user_with_null_roles(self, client, async_db):
        """Test login with user that has null roles defaults to user role"""
        user = User(
            email="nullroles@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            roles=None,
        )
        async_db.add(user)
        await async_db.commit()

        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "nullroles@example.com", "password": "TestPassword123!"},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_user_with_empty_roles(self, client, async_db):
        """Test login with user that has empty roles string"""
        user = User(
            email="emptyroles@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            roles="",
        )
        async_db.add(user)
        await async_db.commit()

        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "emptyroles@example.com", "password": "TestPassword123!"},
        )

        # Empty string fails json.loads, so defaults to ["user"]
        assert response.status_code == 200


class TestTokenRefresh:
    """Test token refresh endpoint"""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client, test_user):
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
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, client, test_user):
        """Test refresh with access token instead of refresh token fails"""
        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["access_token"]},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client):
        """Test refresh with invalid token fails"""
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_disabled_user(self, client, async_db):
        """Test refresh fails if user was disabled after login"""
        # Create user and login
        user = User(
            email="todisable@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            roles='["user"]',
        )
        async_db.add(user)
        await async_db.commit()
        await async_db.refresh(user)

        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "todisable@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        # Disable the user
        user.is_active = False
        await async_db.commit()

        # Try to refresh
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_user_with_null_roles(self, client, async_db):
        """Test refresh with user that has null roles"""
        user = User(
            email="refreshnull@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            roles=None,
        )
        async_db.add(user)
        await async_db.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "refreshnull@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        # Refresh
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )

        assert response.status_code == 200


class TestCurrentUser:
    """Test /me endpoint"""

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, test_user):
        """Test getting current user info"""
        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_current_user_no_full_name(self, client, async_db):
        """Test /me for user without full_name"""
        user = User(
            email="nofullname@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            full_name=None,
            roles='["user"]',
        )
        async_db.add(user)
        await async_db.commit()

        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "nofullname@example.com", "password": "TestPassword123!"},
        )
        tokens = login_response.json()

        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] is None

    @pytest.mark.asyncio
    async def test_get_current_user_no_auth(self, client):
        """Test /me without auth fails"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client):
        """Test /me with invalid token fails"""
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_malformed_auth_header(self, client):
        """Test /me with malformed auth header"""
        response = await client.get("/api/v1/auth/me", headers={"Authorization": "NotBearer token"})

        assert response.status_code == 401
