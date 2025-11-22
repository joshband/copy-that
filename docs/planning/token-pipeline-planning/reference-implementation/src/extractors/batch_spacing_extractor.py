"""
REFERENCE IMPLEMENTATION - Batch Spacing Extractor

This is REFERENCE CODE for planning purposes. It demonstrates how to evolve
the existing BatchColorExtractor pattern for spacing token extraction.

NOTE: This code is not production-ready. It serves as a blueprint for
implementing batch spacing extraction in the actual codebase.

TODO: Integrate with existing copy_that.application module structure
TODO: Add database model for SpacingToken persistence
TODO: Add SSE streaming support for progress updates
"""

import asyncio
import json
import logging

# TODO: Update imports when integrated into main codebase
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).parent.parent))

from aggregators.spacing_aggregator import AggregatedSpacingToken, SpacingAggregator
from extractors.spacing_extractor import AISpacingExtractor
from models.spacing_token import SpacingToken

logger = logging.getLogger(__name__)


class BatchSpacingExtractor:
    """
    Extract and aggregate spacing tokens from multiple images.

    Follows the pattern of BatchColorExtractor from copy_that.application.batch_extractor.

    Features:
    - Semaphore-controlled concurrency for API rate limiting
    - Aggregation via SpacingAggregator
    - Database persistence support
    - Progress tracking

    Example:
        >>> extractor = BatchSpacingExtractor(max_concurrent=3)
        >>> tokens, stats = await extractor.extract_batch(
        ...     image_urls=["url1.png", "url2.png", "url3.png"],
        ...     max_tokens=15,
        ...     similarity_threshold=10.0
        ... )
        >>> print(f"Extracted {len(tokens)} unique spacing values")
    """

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize batch extractor.

        Args:
            max_concurrent: Max concurrent image processing (API rate limits)
        """
        self.max_concurrent = max_concurrent
        self.extractor = AISpacingExtractor()

    async def extract_batch(
        self,
        image_urls: list[str],
        max_tokens: int = 15,
        similarity_threshold: float = 10.0,
    ) -> tuple[list[AggregatedSpacingToken], dict]:
        """
        Extract spacing from multiple images and aggregate.

        Args:
            image_urls: List of image URLs to extract from
            max_tokens: Max spacing tokens per image
            similarity_threshold: Percentage threshold for deduplication

        Returns:
            Tuple of (aggregated_tokens, statistics)

        Example:
            >>> extractor = BatchSpacingExtractor()
            >>> tokens, stats = await extractor.extract_batch(
            ...     ["design1.png", "design2.png"],
            ...     max_tokens=15
            ... )
            >>> print(f"Base unit: {stats['base_unit']}px")
            >>> print(f"Scale system: {stats['scale_system']}")
        """
        logger.info(f"Starting batch extraction for {len(image_urls)} images")

        # Extract spacing from all images (respecting concurrency limit)
        spacing_batch = await self._extract_all_images(image_urls, max_tokens)

        # Aggregate results
        library = SpacingAggregator.aggregate_batch(spacing_batch, similarity_threshold)

        # Suggest roles based on scale position
        library = SpacingAggregator.suggest_token_roles(library)

        logger.info(f"Batch extraction complete: {len(library.tokens)} unique spacing values")
        return library.tokens, library.statistics

    async def extract_batch_with_progress(
        self,
        image_urls: list[str],
        max_tokens: int = 15,
        similarity_threshold: float = 10.0,
        progress_callback: callable = None,
    ) -> tuple[list[AggregatedSpacingToken], dict]:
        """
        Extract spacing with progress callbacks for UI updates.

        Args:
            image_urls: List of image URLs
            max_tokens: Max tokens per image
            similarity_threshold: Deduplication threshold
            progress_callback: Async callback(current, total, status)

        Returns:
            Tuple of (aggregated_tokens, statistics)
        """
        logger.info(f"Starting batch extraction with progress for {len(image_urls)} images")

        total = len(image_urls)
        spacing_batch = []

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def extract_with_progress(url: str, index: int) -> tuple[int, list[SpacingToken]]:
            async with semaphore:
                try:
                    if progress_callback:
                        await progress_callback(index, total, f"Extracting from image {index + 1}")

                    spacings = await self._extract_single_image(url, max_tokens, index)

                    if progress_callback:
                        await progress_callback(index + 1, total, f"Completed image {index + 1}")

                    return index, spacings
                except Exception as e:
                    logger.error(f"Failed to extract {url}: {e}")
                    if progress_callback:
                        await progress_callback(index + 1, total, f"Failed image {index + 1}: {e}")
                    return index, []

        # Extract all images concurrently
        tasks = [extract_with_progress(url, i) for i, url in enumerate(image_urls)]
        results = await asyncio.gather(*tasks)

        # Sort by original index
        results.sort(key=lambda x: x[0])
        spacing_batch = [spacings for _, spacings in results]

        if progress_callback:
            await progress_callback(total, total, "Aggregating results...")

        # Aggregate
        library = SpacingAggregator.aggregate_batch(spacing_batch, similarity_threshold)
        library = SpacingAggregator.suggest_token_roles(library)

        if progress_callback:
            await progress_callback(total, total, "Complete")

        return library.tokens, library.statistics

    async def _extract_all_images(
        self,
        image_urls: list[str],
        max_tokens: int,
    ) -> list[list[SpacingToken]]:
        """
        Extract spacing from all images with concurrency control.

        Args:
            image_urls: List of URLs
            max_tokens: Max tokens per image

        Returns:
            List of spacing lists (one per image)
        """
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def extract_with_limit(url: str, index: int) -> tuple[int, list[SpacingToken]]:
            async with semaphore:
                try:
                    spacings = await self._extract_single_image(url, max_tokens, index)
                    return index, spacings
                except Exception as e:
                    logger.error(f"Failed to extract {url}: {e}")
                    return index, []

        # Extract all images concurrently
        tasks = [extract_with_limit(url, i) for i, url in enumerate(image_urls)]
        results = await asyncio.gather(*tasks)

        # Sort by original index to maintain order
        results.sort(key=lambda x: x[0])
        spacing_batch = [spacings for _, spacings in results]

        return spacing_batch

    async def _extract_single_image(
        self,
        image_url: str,
        max_tokens: int,
        image_index: int,
    ) -> list[SpacingToken]:
        """
        Extract spacing from a single image.

        Args:
            image_url: Image URL
            max_tokens: Max tokens to extract
            image_index: Index for logging

        Returns:
            List of extracted SpacingToken objects
        """
        logger.info(f"Extracting spacing from image {image_index + 1}: {image_url}")

        # Run synchronous extraction in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: self.extractor.extract_spacing_from_image_url(image_url, max_tokens)
        )

        logger.info(f"Extracted {len(result.tokens)} spacing values from image {image_index + 1}")
        return result.tokens

    async def persist_aggregated_library(
        self,
        db: AsyncSession,
        library_id: int,
        project_id: int,
        aggregated_tokens: list[AggregatedSpacingToken],
        statistics: dict,
    ) -> int:
        """
        Persist aggregated spacing tokens to database.

        Args:
            db: Database session
            library_id: TokenLibrary ID to associate tokens with
            project_id: Project ID for audit trail
            aggregated_tokens: Aggregated token objects
            statistics: Aggregation statistics

        Returns:
            Count of persisted tokens

        Note:
            This requires a SpacingToken database model to be defined.
            See copy_that.domain.models for the pattern.

        TODO: Define DBSpacingToken model in copy_that.domain.models
        """
        logger.info(f"Persisting {len(aggregated_tokens)} aggregated spacing tokens")

        # Prepare database records
        token_records = []
        for token in aggregated_tokens:
            record = {
                "project_id": project_id,
                "library_id": library_id,
                "value_px": token.value_px,
                "value_rem": token.value_rem,
                "name": token.name,
                "confidence": token.confidence,
                "semantic_role": token.semantic_role,
                "spacing_type": token.spacing_type,
                "role": token.role,
                "grid_aligned": token.grid_aligned,
                "base_unit": token.base_unit,
                "provenance": json.dumps(token.provenance),
                "merged_values": json.dumps(token.merged_values),
            }
            token_records.append(record)

        # TODO: Replace with actual DBSpacingToken model
        # This is a placeholder showing the pattern
        # batch_size = 100
        # for i in range(0, len(token_records), batch_size):
        #     batch = token_records[i : i + batch_size]
        #     await db.execute(insert(DBSpacingToken).values(batch))
        # await db.commit()

        # For reference implementation, just log what would be persisted
        logger.info(f"Would persist {len(token_records)} spacing tokens to database")
        logger.debug(f"Statistics: {statistics}")

        return len(token_records)


# Convenience function for simple batch extraction


async def extract_spacing_batch(
    image_urls: list[str],
    max_tokens: int = 15,
    similarity_threshold: float = 10.0,
    max_concurrent: int = 3,
) -> tuple[list[AggregatedSpacingToken], dict]:
    """
    Quick function to extract spacing from multiple images.

    Args:
        image_urls: List of image URLs
        max_tokens: Max tokens per image
        similarity_threshold: Deduplication threshold (percentage)
        max_concurrent: Max concurrent extractions

    Returns:
        Tuple of (aggregated_tokens, statistics)

    Example:
        >>> tokens, stats = await extract_spacing_batch(
        ...     ["design1.png", "design2.png"],
        ...     max_tokens=15
        ... )
        >>> for token in tokens:
        ...     print(f"{token.name}: {token.value_px}px")
    """
    extractor = BatchSpacingExtractor(max_concurrent=max_concurrent)
    return await extractor.extract_batch(image_urls, max_tokens, similarity_threshold)
