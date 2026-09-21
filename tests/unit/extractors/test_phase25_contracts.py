"""Phase 2.5 adapter/orchestrator contracts — must match color pattern."""

from __future__ import annotations

import inspect
from io import BytesIO

import pytest
from PIL import Image

from copy_that.extractors.shadow.adapters import (
    AIShadowExtractorAdapter,
    CVShadowExtractorAdapter,
)
from copy_that.extractors.spacing.adapters import CVSpacingExtractorAdapter
from copy_that.extractors.typography.adapters import (
    AITypographyExtractorAdapter,
    CVTypographyExtractorAdapter,
)


@pytest.fixture
def sample_png_bytes() -> bytes:
    img = Image.new("RGB", (32, 32), color=(200, 100, 50))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_spacing_has_ai_adapter_export():
    from copy_that.extractors.spacing import adapters as sa

    assert hasattr(sa, "AISpacingExtractorAdapter"), "missing AI spacing adapter"


def test_adapters_expose_name_and_async_extract():
    from copy_that.extractors.spacing.adapters import AISpacingExtractorAdapter

    for cls in (
        CVSpacingExtractorAdapter,
        AISpacingExtractorAdapter,
        CVTypographyExtractorAdapter,
        AITypographyExtractorAdapter,
        CVShadowExtractorAdapter,
        AIShadowExtractorAdapter,
    ):
        assert isinstance(cls().name, str)
        assert inspect.iscoroutinefunction(cls.extract)


@pytest.mark.asyncio
async def test_typography_ai_adapter_accepts_bytes_without_missing_method(sample_png_bytes):
    adapter = AITypographyExtractorAdapter()
    # Must not raise AttributeError for extract_typography_from_bytes
    with pytest.raises(Exception) as exc:
        await adapter.extract(sample_png_bytes)
    assert "extract_typography_from_bytes" not in str(exc.value)


def test_shadow_adapters_normalize_to_shadow_style(sample_png_bytes):
    from copy_that.extractors.shadow.ai_extractor import ExtractedShadowToken
    from copy_that.extractors.shadow.extractor import ShadowStyle
    from copy_that.extractors.shadow.token_bridge import extracted_to_shadow_style

    token = ExtractedShadowToken(
        x_offset=2.0,
        y_offset=4.0,
        blur_radius=8.0,
        spread_radius=0.0,
        color_hex="#000000",
        opacity=0.25,
        shadow_type="drop",
        semantic_name="subtle-drop",
        confidence=0.9,
    )
    style = extracted_to_shadow_style(token)
    assert isinstance(style, ShadowStyle)
    assert style.x == 2.0
    assert style.y == 4.0
    assert style.blur == 8.0
    assert style.confidence == 0.9
