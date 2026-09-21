"""
End-to-End Tests for Multi-Extractor Spacing Extraction Pipeline

CV-only adapters for CI (no API keys required).
"""

from pathlib import Path

import pytest
import pytest_asyncio

from copy_that.extractors.spacing.adapters import CVSpacingExtractorAdapter
from copy_that.extractors.spacing.orchestrator import (
    SpacingAggregator,
    SpacingExtractionOrchestrator,
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
async def spacing_orchestrator():
    extractors = [CVSpacingExtractorAdapter(max_tokens=10)]
    return SpacingExtractionOrchestrator(
        extractors=extractors,
        aggregator=SpacingAggregator(pixel_distance_threshold=4.0),
    )


class TestE2ESpacingMultiExtractor:
    @pytest.mark.asyncio
    async def test_extract_jpeg(self, spacing_orchestrator, test_image_paths):
        path = test_image_paths["jpeg"]
        if not path.exists():
            pytest.skip(f"missing {path}")
        result = await spacing_orchestrator.extract_all(path.read_bytes(), "e2e_spacing")
        assert result.total_time_ms > 0
        assert result.failed_extractors == []
        for token in result.aggregated_tokens:
            assert token.extraction_metadata and "extractor_sources" in token.extraction_metadata

    @pytest.mark.asyncio
    async def test_extract_png(self, spacing_orchestrator, test_image_paths):
        path = test_image_paths["png"]
        if not path.exists():
            pytest.skip(f"missing {path}")
        result = await spacing_orchestrator.extract_all(path.read_bytes(), "e2e_spacing_png")
        assert result.total_time_ms > 0
        assert result.failed_extractors == []
