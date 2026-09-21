"""
Unit tests for authorization functions
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from copy_that.infrastructure.security.authorization import (
    get_owned_project,
    get_owned_session,
)


class TestGetOwnedProject:
    """Tests for get_owned_project function"""

    @pytest.mark.asyncio
    async def test_returns_project_when_owner(self):
        """Test that owner can access their project"""
        # Setup mocks
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.roles = ["user"]

        mock_project = MagicMock()
        mock_project.owner_id = "user-123"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        # Call function
        result = await get_owned_project(
            project_id=1,
            db=mock_db,
            current_user=mock_user,
        )

        # Verify
        assert result == mock_project
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_404_when_project_not_found(self):
        """Test 404 error when project doesn't exist"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_owned_project(
                project_id=999,
                db=mock_db,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_raises_403_when_not_owner(self):
        """Test 403 error when user is not the owner"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.roles = ["user"]

        mock_project = MagicMock()
        mock_project.owner_id = "other-user-456"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_owned_project(
                project_id=1,
                db=mock_db,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == 403
        assert "Not authorized" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_admin_can_access_any_project(self):
        """Test that admin can access any project"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "admin-user"
        mock_user.roles = ["user", "admin"]

        mock_project = MagicMock()
        mock_project.owner_id = "other-user-456"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        result = await get_owned_project(
            project_id=1,
            db=mock_db,
            current_user=mock_user,
        )

        assert result == mock_project

    @pytest.mark.asyncio
    async def test_allows_access_when_no_owner(self):
        """Test that project without owner is accessible"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.roles = ["user"]

        mock_project = MagicMock()
        mock_project.owner_id = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        result = await get_owned_project(
            project_id=1,
            db=mock_db,
            current_user=mock_user,
        )

        assert result == mock_project


class TestGetOwnedSession:
    """Tests for get_owned_session function"""

    @pytest.mark.asyncio
    async def test_returns_session_when_owner(self):
        """Test that owner can access their session"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.roles = ["user"]

        mock_project = MagicMock()
        mock_project.owner_id = "user-123"

        mock_session = MagicMock()
        mock_session.project = mock_project

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result

        result = await get_owned_session(
            session_id=1,
            db=mock_db,
            current_user=mock_user,
        )

        assert result == mock_session

    @pytest.mark.asyncio
    async def test_raises_404_when_session_not_found(self):
        """Test 404 error when session doesn't exist"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_owned_session(
                session_id=999,
                db=mock_db,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_raises_403_when_not_owner(self):
        """Test 403 error when user is not the owner"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.roles = ["user"]

        mock_project = MagicMock()
        mock_project.owner_id = "other-user-456"

        mock_session = MagicMock()
        mock_session.project = mock_project

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_owned_session(
                session_id=1,
                db=mock_db,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == 403
        assert "Not authorized" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_admin_can_access_any_session(self):
        """Test that admin can access any session"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "admin-user"
        mock_user.roles = ["user", "admin"]

        mock_project = MagicMock()
        mock_project.owner_id = "other-user-456"

        mock_session = MagicMock()
        mock_session.project = mock_project

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result

        result = await get_owned_session(
            session_id=1,
            db=mock_db,
            current_user=mock_user,
        )

        assert result == mock_session

    @pytest.mark.asyncio
    async def test_allows_access_when_session_has_no_project(self):
        """Test that session without project is accessible"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.roles = ["user"]

        mock_session = MagicMock()
        mock_session.project = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result

        result = await get_owned_session(
            session_id=1,
            db=mock_db,
            current_user=mock_user,
        )

        assert result == mock_session

    @pytest.mark.asyncio
    async def test_allows_access_when_project_has_no_owner(self):
        """Test that session with unowned project is accessible"""
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.roles = ["user"]

        mock_project = MagicMock()
        mock_project.owner_id = None

        mock_session = MagicMock()
        mock_session.project = mock_project

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result

        result = await get_owned_session(
            session_id=1,
            db=mock_db,
            current_user=mock_user,
        )

        assert result == mock_session
