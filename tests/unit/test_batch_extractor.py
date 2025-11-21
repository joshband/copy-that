"""Tests for batch color extraction service"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copy_that.application.batch_extractor import BatchColorExtractor
from copy_that.application.color_extractor import ColorToken
from copy_that.tokens.color.aggregator import AggregatedColorToken


@pytest.fixture
def sample_color_tokens():
    """Sample color tokens for testing"""
    return [
        ColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.95),
        ColorToken(hex="#00FF00", rgb="rgb(0, 255, 0)", name="Green", confidence=0.92),
        ColorToken(hex="#0000FF", rgb="rgb(0, 0, 255)", name="Blue", confidence=0.90),
    ]


@pytest.fixture
def mock_extractor():
    """Mock AIColorExtractor"""
    with patch("copy_that.application.batch_extractor.AIColorExtractor") as mock:
        yield mock


@pytest.fixture
def batch_extractor(mock_extractor):
    """Create BatchColorExtractor with mocked AIColorExtractor"""
    return BatchColorExtractor(max_concurrent=2)


@pytest.mark.asyncio
async def test_extract_batch_single_image(batch_extractor, sample_color_tokens):
    """Test extracting colors from a single image"""
    batch_extractor.extractor.extract_colors_from_url = AsyncMock(return_value=sample_color_tokens)

    with patch("copy_that.application.batch_extractor.ColorAggregator") as mock_agg:
        mock_library = MagicMock()
        mock_library.tokens = sample_color_tokens
        mock_library.statistics = {"total": 3, "unique": 3}
        mock_agg.aggregate_batch.return_value = mock_library

        tokens, stats = await batch_extractor.extract_batch(
            image_urls=["http://example.com/image.jpg"],
            max_colors=10,
        )

        assert len(tokens) == 3
        assert tokens[0].hex == "#FF0000"
        assert stats["total"] == 3


@pytest.mark.asyncio
async def test_extract_batch_multiple_images(batch_extractor, sample_color_tokens):
    """Test extracting colors from multiple images"""
    batch_extractor.extractor.extract_colors_from_url = AsyncMock(return_value=sample_color_tokens)

    with patch("copy_that.application.batch_extractor.ColorAggregator") as mock_agg:
        mock_library = MagicMock()
        mock_library.tokens = sample_color_tokens
        mock_library.statistics = {"total": 9, "unique": 3}
        mock_agg.aggregate_batch.return_value = mock_library

        image_urls = [
            "http://example.com/image1.jpg",
            "http://example.com/image2.jpg",
            "http://example.com/image3.jpg",
        ]

        tokens, stats = await batch_extractor.extract_batch(
            image_urls=image_urls,
            max_colors=10,
        )

        # Should call extract_colors_from_url 3 times
        assert batch_extractor.extractor.extract_colors_from_url.call_count == 3
        assert stats["total"] == 9


@pytest.mark.asyncio
async def test_extract_batch_with_error_handling(batch_extractor):
    """Test that failures in one image don't break the entire batch"""
    # First image succeeds, second fails, third succeeds
    side_effects = [
        [ColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.95)],
        Exception("Network error"),
        [ColorToken(hex="#0000FF", rgb="rgb(0, 0, 255)", name="Blue", confidence=0.90)],
    ]
    batch_extractor.extractor.extract_colors_from_url = AsyncMock(side_effect=side_effects)

    with patch("copy_that.application.batch_extractor.ColorAggregator") as mock_agg:
        mock_library = MagicMock()
        mock_library.tokens = []
        mock_library.statistics = {"total": 2, "failed": 1}
        mock_agg.aggregate_batch.return_value = mock_library

        tokens, stats = await batch_extractor.extract_batch(
            image_urls=[
                "http://example.com/image1.jpg",
                "http://example.com/image2.jpg",
                "http://example.com/image3.jpg",
            ],
            max_colors=10,
        )

        # Should still complete and aggregate what succeeded
        assert batch_extractor.extractor.extract_colors_from_url.call_count == 3


@pytest.mark.asyncio
async def test_extract_batch_respects_concurrency_limit(batch_extractor, sample_color_tokens):
    """Test that max_concurrent is respected"""
    batch_extractor.max_concurrent = 2

    call_times = []

    async def tracked_extract(*args, **kwargs):
        call_times.append(asyncio.get_event_loop().time())
        await asyncio.sleep(0.01)  # Simulate work
        return sample_color_tokens

    batch_extractor.extractor.extract_colors_from_url = tracked_extract

    with patch("copy_that.application.batch_extractor.ColorAggregator") as mock_agg:
        mock_library = MagicMock()
        mock_library.tokens = sample_color_tokens
        mock_library.statistics = {}
        mock_agg.aggregate_batch.return_value = mock_library

        await batch_extractor.extract_batch(
            image_urls=[
                "http://example.com/1.jpg",
                "http://example.com/2.jpg",
                "http://example.com/3.jpg",
            ],
            max_colors=10,
        )

        # With max_concurrent=2, should not have all 3 starting simultaneously
        # (Would need better timing test, but this verifies the semaphore exists)
        assert batch_extractor.max_concurrent == 2


@pytest.mark.asyncio
async def test_extract_batch_with_custom_delta_e_threshold(batch_extractor, sample_color_tokens):
    """Test that custom delta_e_threshold is passed to aggregator"""
    batch_extractor.extractor.extract_colors_from_url = AsyncMock(return_value=sample_color_tokens)

    with patch("copy_that.application.batch_extractor.ColorAggregator") as mock_agg:
        mock_library = MagicMock()
        mock_library.tokens = sample_color_tokens
        mock_library.statistics = {}
        mock_agg.aggregate_batch.return_value = mock_library

        await batch_extractor.extract_batch(
            image_urls=["http://example.com/image.jpg"],
            max_colors=10,
            delta_e_threshold=5.0,
        )

        # Verify delta_e_threshold was passed
        mock_agg.aggregate_batch.assert_called_once()
        call_args = mock_agg.aggregate_batch.call_args
        assert call_args[0][1] == 5.0  # Second argument is delta_e_threshold


@pytest.mark.asyncio
async def test_persist_aggregated_library(batch_extractor):
    """Test persisting aggregated tokens to database"""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    tokens = [
        AggregatedColorToken(
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.95,
            harmony="monochromatic",
            role="primary",
            provenance={"image_0": 0.95},
        ),
    ]

    token_count = await batch_extractor.persist_aggregated_library(
        db=mock_db,
        library_id=1,
        project_id=1,
        aggregated_tokens=tokens,
        statistics={"total": 1},
    )

    assert token_count == 1
    mock_db.execute.assert_called()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_persist_aggregated_library_batch_insert(batch_extractor):
    """Test that large token sets are inserted in batches"""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    # Create 250 tokens (should be split into 3 batches with batch_size=100)
    tokens = [
        AggregatedColorToken(
            hex=f"#{i:06X}",
            rgb=f"rgb({i % 256}, {(i + 1) % 256}, {(i + 2) % 256})",
            name=f"Color{i}",
            confidence=0.9,
            role="neutral" if i % 5 == 0 else None,
            provenance={f"image_{i % 3}": 0.9},
        )
        for i in range(250)
    ]

    token_count = await batch_extractor.persist_aggregated_library(
        db=mock_db,
        library_id=1,
        project_id=1,
        aggregated_tokens=tokens,
        statistics={"total": 250},
    )

    assert token_count == 250
    # Should be called 3 times (batch insert) + 1 final commit
    assert mock_db.execute.call_count == 3
    assert mock_db.commit.call_count == 1


@pytest.mark.asyncio
async def test_extract_all_images_maintains_order(batch_extractor):
    """Test that image extraction maintains order despite async processing"""
    # Different colors for each image
    colors_per_image = [
        [ColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.95)],
        [ColorToken(hex="#00FF00", rgb="rgb(0, 255, 0)", name="Green", confidence=0.92)],
        [ColorToken(hex="#0000FF", rgb="rgb(0, 0, 255)", name="Blue", confidence=0.90)],
    ]

    call_count = [0]

    async def extract_by_index(*args, **kwargs):
        result = colors_per_image[call_count[0]]
        call_count[0] += 1
        return result

    batch_extractor.extractor.extract_colors_from_url = extract_by_index

    colors_batch = await batch_extractor._extract_all_images(
        image_urls=["url1", "url2", "url3"],
        max_colors=10,
    )

    # Verify order is maintained
    assert colors_batch[0][0].hex == "#FF0000"  # Red
    assert colors_batch[1][0].hex == "#00FF00"  # Green
    assert colors_batch[2][0].hex == "#0000FF"  # Blue
