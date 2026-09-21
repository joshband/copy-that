"""
End-to-End Tests for Multi-Extractor Typography Extraction Pipeline

CV-only adapters for CI (no API keys required).
"""

from pathlib import Path

import pytest
import pytest_asyncio

from copy_that.extractors.typography.adapters import CVTypographyExtractorAdapter
from copy_that.extractors.typography.orchestrator import (
    TypographyAggregator,
    TypographyExtractionOrchestrator,
)


@pytest.fixture
def test_image_paths():
    project_root = Path(__file__).parent.parent.parent.parent.parent
    test_dir = project_root / "test_images"
    return {
        "jpeg": test_dir / "IMG_8405.jpeg",
        # Second committed fixture (PNG pipeline outputs are not committed)
        "png": test_dir / "IMG_8597.jpeg",
    }


@pytest_asyncio.fixture
async def typography_orchestrator():
    extractors = [CVTypographyExtractorAdapter()]
    return TypographyExtractionOrchestrator(
        extractors=extractors,
        aggregator=TypographyAggregator(font_size_threshold=3),
    )


class TestE2ETypographyMultiExtractor:
    @pytest.mark.asyncio
    async def test_extract_jpeg(self, typography_orchestrator, test_image_paths):
        path = test_image_paths["jpeg"]
        if not path.exists():
            pytest.skip(f"missing {path}")
        result = await typography_orchestrator.extract_all(path.read_bytes(), "e2e_typography")
        assert result.total_time_ms > 0
        assert result.failed_extractors == []
        for token in result.aggregated_tokens:
            assert token.extraction_metadata and "extractor_sources" in token.extraction_metadata

    @pytest.mark.asyncio
    async def test_extract_png(self, typography_orchestrator, test_image_paths):
        path = test_image_paths["png"]
        if not path.exists():
            pytest.skip(f"missing {path}")
        result = await typography_orchestrator.extract_all(path.read_bytes(), "e2e_typography_png")
        assert result.total_time_ms > 0
        assert result.failed_extractors == []
