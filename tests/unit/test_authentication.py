"""
Unit tests for authentication module
"""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from copy_that.infrastructure.security.authentication import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    get_current_user,
    get_password_hash,
    require_roles,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing functions"""

    def test_verify_password_correct(self):
        """Test that correct password verifies"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword", hashed) is False


class TestTokenCreation:
    """Tests for token creation functions"""

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry"""
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(hours=2))

        assert isinstance(token, str)

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_pair(self):
        """Test creating both access and refresh tokens"""
        result = create_token_pair("user-123", "test@example.com", ["user"])

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"


class TestTokenDecoding:
    """Tests for token decoding"""

    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        data = {"sub": "user-123", "email": "test@example.com", "roles": ["user"]}
        token = create_access_token(data)

        decoded = decode_token(token)

        assert decoded.user_id == "user-123"
        assert decoded.email == "test@example.com"
        assert decoded.roles == ["user"]

    def test_decode_token_missing_user_id(self):
        """Test that token without user ID raises error"""
        import time
        from jose import jwt

        from copy_that.infrastructure.security.authentication import ALGORITHM, SECRET_KEY

        # Create token without sub claim but with valid exp
        token = jwt.encode(
            {"email": "test@example.com", "exp": int(time.time()) + 3600},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)

        assert exc_info.value.status_code == 401
        assert "missing user ID" in exc_info.value.detail

    def test_decode_invalid_token(self):
        """Test that invalid token raises error"""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")

        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Tests for get_current_user dependency"""

    @pytest.mark.asyncio
    async def test_returns_user_when_valid(self):
        """Test that valid token returns user"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Create valid token
        token_pair = create_token_pair("user-123", "test@example.com", ["user"])

        result = await get_current_user(token_pair.access_token, mock_db)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_raises_401_when_user_not_found(self):
        """Test that 401 is raised when user not found"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        token_pair = create_token_pair("nonexistent", "test@example.com", ["user"])

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token_pair.access_token, mock_db)

        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_raises_403_when_user_inactive(self):
        """Test that 403 is raised when user is inactive"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.is_active = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        token_pair = create_token_pair("user-123", "test@example.com", ["user"])

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token_pair.access_token, mock_db)

        assert exc_info.value.status_code == 403
        assert "disabled" in exc_info.value.detail


class TestRequireRoles:
    """Tests for require_roles dependency factory"""

    @pytest.mark.asyncio
    async def test_allows_user_with_required_role(self):
        """Test that user with required role is allowed"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.roles = ["user", "admin"]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        token_pair = create_token_pair("user-123", "test@example.com", ["admin"])

        role_checker = require_roles("admin")
        result = await role_checker(token_pair.access_token, mock_db)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_denies_user_without_required_role(self):
        """Test that user without required role is denied"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.roles = ["user"]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        token_pair = create_token_pair("user-123", "test@example.com", ["user"])

        role_checker = require_roles("admin")

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(token_pair.access_token, mock_db)

        assert exc_info.value.status_code == 403
        assert "Requires" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_raises_401_when_user_not_found(self):
        """Test that 401 is raised when user not found"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        token_pair = create_token_pair("nonexistent", "test@example.com", ["user"])

        role_checker = require_roles("admin")

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(token_pair.access_token, mock_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_handles_none_roles(self):
        """Test that None roles are handled correctly"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.roles = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        token_pair = create_token_pair("user-123", "test@example.com", ["user"])

        role_checker = require_roles("admin")

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(token_pair.access_token, mock_db)

        assert exc_info.value.status_code == 403
