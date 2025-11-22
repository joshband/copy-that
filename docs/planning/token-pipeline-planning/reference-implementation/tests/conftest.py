"""
Pytest configuration and shared fixtures for spacing token pipeline tests

REFERENCE IMPLEMENTATION - This is planning/documentation code showing how the
test fixtures should be structured when implemented. This code
is not meant to be run directly but serves as a complete reference for
implementing the actual tests.

This module provides:
1. Database fixtures for testing
2. FastAPI test client fixtures
3. Mock AI response fixtures
4. Sample image fixtures
5. Expected result fixtures
"""

import base64
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Add src directory to path so imports work
# When integrated, adjust this path:
# src_path = Path(__file__).parent.parent.parent.parent / "src"
# sys.path.insert(0, str(src_path))

# When implemented, these would be actual imports:
# from copy_that.infrastructure.database import Base, get_db
# from copy_that.interfaces.api.main import app
# import copy_that.domain.models  # Register all models


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db():
    """
    Create an in-memory SQLite database for testing.

    This fixture:
    - Creates a fresh database for each test
    - Creates all tables including spacing_tokens
    - Yields the session
    - Cleans up after the test
    """
    # When implemented:
    # engine = create_async_engine(
    #     "sqlite+aiosqlite:///:memory:",
    #     connect_args={"check_same_thread": False},
    #     poolclass=StaticPool,
    #     echo=False,
    # )

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    # from sqlalchemy.ext.asyncio import async_sessionmaker
    # TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # async with TestSessionLocal() as session:
    #     yield session

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

    # await engine.dispose()

    # Mock implementation for reference
    yield MagicMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def async_client(test_db):
    """
    Create an async HTTP client for testing FastAPI endpoints.

    This fixture:
    - Patches the database dependency to use the test database
    - Provides an AsyncClient for making requests
    """
    # When implemented:
    # async def override_get_db():
    #     yield test_db

    # from httpx import ASGITransport

    # app.dependency_overrides[get_db] = override_get_db

    # transport = ASGITransport(app=app)
    # async with AsyncClient(transport=transport, base_url="http://test") as client:
    #     yield client

    # app.dependency_overrides.clear()

    # Mock implementation for reference
    yield MagicMock(spec=AsyncClient)


# =============================================================================
# Mock AI Client Fixtures
# =============================================================================

@pytest.fixture
def mock_anthropic_client():
    """
    Mock Anthropic client for testing without real API calls.
    """
    with patch("anthropic.Anthropic") as mock_class:
        mock_client = MagicMock()
        mock_class.return_value = mock_client

        # Setup default response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps([
            {
                "value": 16,
                "type": "padding",
                "context": "card padding",
                "design_intent": "comfortable spacing"
            }
        ]))]
        mock_client.messages.create.return_value = mock_response

        yield mock_client


@pytest.fixture
def mock_openai_client():
    """
    Mock OpenAI client for testing without real API calls.
    """
    with patch("openai.AsyncOpenAI") as mock_class:
        mock_client = MagicMock()
        mock_class.return_value = mock_client

        # Setup default response
        async_mock = AsyncMock()
        async_mock.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content=json.dumps([
                        {
                            "value": 16,
                            "type": "padding",
                            "context": "card padding",
                            "design_intent": "comfortable spacing"
                        }
                    ])
                )
            )]
        )
        mock_client.chat.completions.create = async_mock

        yield mock_client


@pytest.fixture
def mock_api_key(monkeypatch):
    """
    Set mock API keys for testing without real API calls.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_only")
    monkeypatch.setenv("OPENAI_API_KEY", "test_only")
    return {
        "anthropic": "test_only",
        "openai": "test_only"
    }


# =============================================================================
# Sample Image Fixtures
# =============================================================================

@pytest.fixture
def sample_base64_image():
    """
    Provide a sample base64 encoded image for testing.

    Returns a minimal valid PNG image.
    """
    # 1x1 pixel transparent PNG
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
        0x42, 0x60, 0x82
    ])
    return base64.b64encode(png_data).decode('utf-8')


@pytest.fixture
def sample_image_urls():
    """
    Provide sample image URLs for batch testing.
    """
    return [
        "https://example.com/design1.png",
        "https://example.com/design2.png",
        "https://example.com/design3.png",
    ]


def load_test_image(filename: str = "test_image.png") -> str:
    """
    Helper function to load a test image from fixtures directory.

    Args:
        filename: Name of the image file in the test fixtures directory

    Returns:
        Base64 encoded image data
    """
    # When implemented:
    # fixtures_dir = Path(__file__).parent / "fixtures"
    # image_path = fixtures_dir / filename
    # with open(image_path, "rb") as f:
    #     return base64.b64encode(f.read()).decode('utf-8')

    # Return minimal PNG for reference
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
        0x44, 0xAE, 0x42, 0x60, 0x82
    ])
    return base64.b64encode(png_data).decode('utf-8')


# =============================================================================
# Spacing Token Fixtures
# =============================================================================

@pytest.fixture
def spacing_token_factory():
    """
    Factory fixture for creating SpacingToken test instances.

    Usage:
        token = spacing_token_factory(value_px=16, confidence=0.95)
    """
    def _create_token(**kwargs) -> Any:
        defaults = {
            "value_px": 16,
            "value_rem": 1.0,
            "value_em": 1.0,
            "scale": "md",
            "base_unit": 4,
            "multiplier": 4.0,
            "name": "medium-padding",
            "spacing_type": "padding",
            "design_intent": "comfortable spacing",
            "use_case": "general padding",
            "context": "card component",
            "confidence": 0.85,
            "is_grid_compliant": True,
            "rhythm_consistency": "consistent",
            "responsive_scales": {
                "mobile": 12,
                "tablet": 16,
                "desktop": 20,
                "widescreen": 24
            },
            "semantic_names": {
                "simple": "md",
                "descriptive": "medium-padding",
                "contextual": "card-padding"
            },
            "related_to": None,
            "component_usage": None,
            "extraction_metadata": {
                "computation_version": "1.0",
                "algorithms_used": ["unit_conversion", "scale_detection"]
            }
        }
        defaults.update(kwargs)

        # When implemented, return actual SpacingToken:
        # from copy_that.tokens.spacing.models import SpacingToken
        # return SpacingToken(**defaults)

        # For reference, return a MagicMock with the expected attributes
        token = MagicMock()
        for key, value in defaults.items():
            setattr(token, key, value)

        # Add validation behavior
        if defaults["confidence"] > 1 or defaults["confidence"] < 0:
            raise ValueError("Confidence must be between 0 and 1")

        return token

    return _create_token


@pytest.fixture
def sample_spacing_tokens():
    """
    Provide a list of sample spacing tokens for testing.
    """
    return [
        {
            "value_px": 4,
            "value_rem": 0.25,
            "value_em": 0.25,
            "scale": "2xs",
            "base_unit": 4,
            "multiplier": 1.0,
            "name": "tight-padding",
            "spacing_type": "padding",
            "design_intent": "tight spacing",
            "confidence": 0.90,
            "is_grid_compliant": True,
        },
        {
            "value_px": 8,
            "value_rem": 0.5,
            "value_em": 0.5,
            "scale": "xs",
            "base_unit": 8,
            "multiplier": 1.0,
            "name": "compact-padding",
            "spacing_type": "padding",
            "design_intent": "compact touch target",
            "confidence": 0.92,
            "is_grid_compliant": True,
        },
        {
            "value_px": 16,
            "value_rem": 1.0,
            "value_em": 1.0,
            "scale": "md",
            "base_unit": 8,
            "multiplier": 2.0,
            "name": "comfortable-padding",
            "spacing_type": "padding",
            "design_intent": "comfortable breathing room",
            "confidence": 0.95,
            "is_grid_compliant": True,
        },
        {
            "value_px": 24,
            "value_rem": 1.5,
            "value_em": 1.5,
            "scale": "lg",
            "base_unit": 8,
            "multiplier": 3.0,
            "name": "relaxed-margin",
            "spacing_type": "margin",
            "design_intent": "clear separation",
            "confidence": 0.88,
            "is_grid_compliant": True,
        },
        {
            "value_px": 32,
            "value_rem": 2.0,
            "value_em": 2.0,
            "scale": "xl",
            "base_unit": 8,
            "multiplier": 4.0,
            "name": "spacious-gap",
            "spacing_type": "gap",
            "design_intent": "generous layout spacing",
            "confidence": 0.85,
            "is_grid_compliant": True,
        },
    ]


@pytest.fixture
def sample_ai_spacing_response():
    """
    Provide a sample AI response for spacing extraction.
    """
    return json.dumps([
        {
            "value": 8,
            "type": "padding",
            "context": "button internal padding",
            "design_intent": "compact touch target"
        },
        {
            "value": 16,
            "type": "padding",
            "context": "card content padding",
            "design_intent": "comfortable reading space"
        },
        {
            "value": 24,
            "type": "margin",
            "context": "section margin",
            "design_intent": "clear content separation"
        },
        {
            "value": 12,
            "type": "gap",
            "context": "form field gap",
            "design_intent": "related element grouping"
        },
        {
            "value": 32,
            "type": "margin",
            "context": "page section margin",
            "design_intent": "major content division"
        }
    ])


# =============================================================================
# Expected Results Fixtures
# =============================================================================

@pytest.fixture
def expected_scale_mappings():
    """
    Expected scale position mappings for validation.
    """
    return {
        0: "none",
        4: "2xs",
        8: "xs",
        12: "sm",
        16: "md",
        20: "md",
        24: "lg",
        32: "xl",
        40: "xl",
        48: "2xl",
        64: "3xl",
    }


@pytest.fixture
def expected_rem_conversions():
    """
    Expected rem conversion values for validation.
    """
    return {
        4: 0.25,
        8: 0.5,
        12: 0.75,
        16: 1.0,
        20: 1.25,
        24: 1.5,
        32: 2.0,
        40: 2.5,
        48: 3.0,
        64: 4.0,
    }


@pytest.fixture
def expected_base_unit_detection():
    """
    Expected base unit detection results.
    """
    return {
        8: 8,   # Divisible by 8
        16: 8,  # Divisible by 8
        24: 8,  # Divisible by 8
        4: 4,   # Only divisible by 4
        12: 4,  # Only divisible by 4
        20: 4,  # Only divisible by 4
        5: 1,   # Non-standard
        7: 1,   # Non-standard
        9: 1,   # Non-standard
    }


# =============================================================================
# Helper Fixtures
# =============================================================================

@pytest.fixture
def create_test_project(test_db):
    """
    Helper fixture to create a test project.
    """
    async def _create_project(name: str = "Test Project"):
        # When implemented:
        # from copy_that.domain.models import Project
        # project = Project(name=name)
        # test_db.add(project)
        # await test_db.commit()
        # await test_db.refresh(project)
        # return project

        return MagicMock(id=1, name=name)

    return _create_project


@pytest.fixture
def create_test_session(test_db):
    """
    Helper fixture to create a test session.
    """
    async def _create_session(project_id: int = 1, name: str = "Test Session"):
        # When implemented:
        # from copy_that.domain.models import Session
        # session = Session(project_id=project_id, name=name)
        # test_db.add(session)
        # await test_db.commit()
        # await test_db.refresh(session)
        # return session

        return MagicMock(id=1, project_id=project_id, name=name)

    return _create_session


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: marks tests that require real API keys"
    )
