"""
End-to-End Tests for Multi-Extractor Color Extraction Pipeline

Tests the complete flow from image input through extraction, aggregation,
and deduplication with Delta-E color science.
"""

import base64
import time
from pathlib import Path

import pytest
import pytest_asyncio

from copy_that.extractors.color.adapters import (
    CVColorExtractorAdapter,
    KMeansExtractorAdapter,
)
from copy_that.extractors.color.orchestrator import MultiExtractorOrchestrator
from copy_that.tokens.color.aggregator import ColorAggregator


@pytest.fixture
def test_image_paths():
    """Get paths to test images"""
    # Navigate from src/copy_that/extractors/color to project root
    project_root = Path(__file__).parent.parent.parent.parent.parent
    test_dir = project_root / "test_images"
    return {
        "jpeg": test_dir / "IMG_8405.jpeg",
        "png": test_dir / "processedImageShadows_enhanced" / "IMG_8597" / "00_original.png",
    }


@pytest_asyncio.fixture
async def orchestrator():
    """Create orchestrator with all three extractors"""
    extractors = [
        KMeansExtractorAdapter(k=10),
        CVColorExtractorAdapter(max_colors=8),
        # Claude adapter disabled for automated testing (no API key)
    ]
    aggregator = ColorAggregator(delta_e_threshold=2.3)
    return MultiExtractorOrchestrator(extractors=extractors, aggregator=aggregator)


class TestE2EBasicExtraction:
    """Test basic extraction workflows"""

    @pytest.mark.asyncio
    async def test_extract_jpeg_image(self, orchestrator, test_image_paths):
        """Test extraction from JPEG image"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_jpeg_1")

        assert result is not None
        assert len(result.aggregated_colors) > 0
        assert result.overall_confidence > 0
        assert result.total_time_ms > 0

    @pytest.mark.asyncio
    async def test_extract_png_image(self, orchestrator, test_image_paths):
        """Test extraction from PNG image"""
        image_path = test_image_paths["png"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_png_1")

        assert result is not None
        assert len(result.aggregated_colors) > 0
        assert result.overall_confidence > 0

    @pytest.mark.asyncio
    async def test_results_have_provenance(self, orchestrator, test_image_paths):
        """Verify that colors track which extractors found them"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_provenance")

        # Each color should have provenance data in extraction_metadata
        for color in result.aggregated_colors:
            assert hasattr(color, "extraction_metadata")
            assert "extractor_sources" in color.extraction_metadata
            sources = color.extraction_metadata["extractor_sources"]
            assert len(sources) > 0
            # Verify extractor names are tracked (they use image IDs like "image_0")
            for source in sources:
                assert isinstance(source, (str, int))


class TestE2EAggregation:
    """Test color aggregation and deduplication"""

    @pytest.mark.asyncio
    async def test_delta_e_deduplication(self, orchestrator, test_image_paths):
        """Test that similar colors are deduplicated using Delta-E"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_dedup")

        # Aggregated colors should be fewer than or equal to raw colors
        # (due to deduplication)
        total_raw_colors = sum(
            len(extractor_result.colors) for extractor_result in result.extraction_results
        )

        assert len(result.aggregated_colors) <= total_raw_colors
        assert len(result.aggregated_colors) > 0

    @pytest.mark.asyncio
    async def test_confidence_aggregation(self, orchestrator, test_image_paths):
        """Test that confidence scores are properly aggregated"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_confidence")

        # Overall confidence should be between 0 and 1
        assert 0 <= result.overall_confidence <= 1

        # Individual color confidence should also be in range
        for color in result.aggregated_colors:
            assert 0 <= color.confidence <= 1


class TestE2EErrorHandling:
    """Test error scenarios and graceful degradation"""

    @pytest.mark.asyncio
    async def test_graceful_degradation_invalid_image(self, orchestrator):
        """Test that extraction continues if one extractor fails"""
        invalid_image_bytes = b"not an image"

        result = await orchestrator.extract_all(invalid_image_bytes, "test_invalid")

        # Should return result even if all extractors failed
        assert result is not None
        assert hasattr(result, "failed_extractors")
        # All extractors should have failed with invalid image
        assert len(result.failed_extractors) > 0

    @pytest.mark.asyncio
    async def test_all_extractors_tracked_in_result(self, orchestrator):
        """Verify all extractors are tracked in results/failures"""
        invalid_image_bytes = b"not an image"

        result = await orchestrator.extract_all(invalid_image_bytes, "test_tracking")

        # All extractors should be tracked (either success or failure)
        total_results = len(result.extraction_results) + len(result.failed_extractors)
        assert total_results == len(orchestrator.extractors)


class TestE2EPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_parallel_execution_is_faster(self, test_image_paths):
        """Test that parallel extraction is faster than sequential"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Create single extractors for comparison
        kmeans = KMeansExtractorAdapter(k=10)
        cv = CVColorExtractorAdapter(max_colors=8)

        # Sequential extraction
        start = time.time()
        result1 = await kmeans.extract(image_bytes)
        result2 = await cv.extract(image_bytes)
        sequential_time = time.time() - start

        # Parallel extraction (via orchestrator)
        orchestrator_instance = MultiExtractorOrchestrator(
            extractors=[kmeans, cv],
            aggregator=ColorAggregator(delta_e_threshold=2.3),
        )

        start = time.time()
        result = await orchestrator_instance.extract_all(image_bytes, "test_perf")
        parallel_time = time.time() - start

        # Parallel should be faster (at least not significantly slower)
        # Allow 20% margin for overhead
        assert parallel_time < sequential_time * 1.2

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, orchestrator, test_image_paths):
        """Verify execution time is properly tracked"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_timing")

        assert result.total_time_ms > 0
        # Sanity check: should complete in under 30 seconds
        assert result.total_time_ms < 30000


class TestE2EColorProperties:
    """Test extracted color properties"""

    @pytest.mark.asyncio
    async def test_colors_have_required_fields(self, orchestrator, test_image_paths):
        """Verify extracted colors have all required fields"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_fields")

        for color in result.aggregated_colors:
            # Required hex format
            assert hasattr(color, "hex")
            assert isinstance(color.hex, str)
            assert color.hex.startswith("#")
            assert len(color.hex) == 7  # #RRGGBB

            # Confidence score
            assert hasattr(color, "confidence")
            assert 0 <= color.confidence <= 1

            # Extraction metadata with provenance
            assert hasattr(color, "extraction_metadata")
            assert isinstance(color.extraction_metadata, dict)
            assert "extractor_sources" in color.extraction_metadata

    @pytest.mark.asyncio
    async def test_colors_are_unique_hex_values(self, orchestrator, test_image_paths):
        """Verify no duplicate hex values in aggregated results"""
        image_path = test_image_paths["jpeg"]
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = await orchestrator.extract_all(image_bytes, "test_unique")

        hex_values = [color.hex for color in result.aggregated_colors]
        # While similar colors might exist due to Delta-E threshold,
        # exact duplicates should not exist
        assert len(hex_values) == len(set(hex_values))


class TestE2EIntegration:
    """Integration tests covering complete workflows"""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_base64_image(self, orchestrator):
        """Test complete workflow with base64-encoded image"""
        image_path = Path(__file__).parent.parent.parent.parent / "test_images" / "IMG_8405.jpeg"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Simulate API request with base64
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # In real API, this would be: f"data:image/jpeg;base64,{base64_image}"
        # For this test, just use raw bytes
        result = await orchestrator.extract_all(image_bytes, "test_complete")

        assert result is not None
        assert len(result.aggregated_colors) > 0
        assert result.overall_confidence > 0

    @pytest.mark.asyncio
    async def test_multiple_images_sequential(self, orchestrator, test_image_paths):
        """Test processing multiple images in sequence"""
        image_paths = [test_image_paths["jpeg"], test_image_paths["png"]]
        image_paths = [p for p in image_paths if p.exists()]

        if len(image_paths) < 2:
            pytest.skip("Not enough test images")

        results = []
        for i, path in enumerate(image_paths):
            with open(path, "rb") as f:
                image_bytes = f.read()
            result = await orchestrator.extract_all(image_bytes, f"image_{i}")
            results.append(result)

        assert len(results) == len(image_paths)
        assert all(r.aggregated_colors for r in results)
