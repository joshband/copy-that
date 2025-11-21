"""
Batch image extraction service - orchestrates color extraction for multiple images

Handles:
- Parallel/sequential image extraction
- Aggregation of results via ColorAggregator
- Database persistence of aggregated tokens
"""

import asyncio
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from copy_that.application.color_extractor import AIColorExtractor, ColorToken
from copy_that.tokens.color.aggregator import ColorAggregator
from copy_that.domain.models import (
    TokenLibrary,
    ColorToken as DBColorToken,
)

logger = logging.getLogger(__name__)


class BatchColorExtractor:
    """Extract and aggregate colors from multiple images"""

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize batch extractor

        Args:
            max_concurrent: Max concurrent image processing (API rate limits)
        """
        self.max_concurrent = max_concurrent
        self.extractor = AIColorExtractor()

    async def extract_batch(
        self,
        image_urls: List[str],
        max_colors: int = 10,
        delta_e_threshold: float = 2.0,
    ) -> tuple[List[ColorToken], dict]:
        """
        Extract colors from multiple images and aggregate

        Args:
            image_urls: List of image URLs to extract from
            max_colors: Max colors per image
            delta_e_threshold: Delta-E threshold for deduplication

        Returns:
            Tuple of (aggregated_tokens, statistics)
        """
        logger.info(f"Starting batch extraction for {len(image_urls)} images")

        # Extract colors from all images (respecting concurrency limit)
        colors_batch = await self._extract_all_images(image_urls, max_colors)

        # Aggregate results
        library = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold)

        logger.info(f"Batch extraction complete: {len(library.tokens)} unique colors")
        return library.tokens, library.statistics

    async def _extract_all_images(
        self,
        image_urls: List[str],
        max_colors: int,
    ) -> List[List[ColorToken]]:
        """
        Extract colors from all images with concurrency control

        Args:
            image_urls: List of URLs
            max_colors: Max colors per image

        Returns:
            List of color lists (one per image)
        """
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def extract_with_limit(url: str, index: int) -> tuple[int, List[ColorToken]]:
            async with semaphore:
                try:
                    colors = await self._extract_single_image(url, max_colors, index)
                    return index, colors
                except Exception as e:
                    logger.error(f"Failed to extract {url}: {e}")
                    return index, []

        # Extract all images concurrently
        tasks = [
            extract_with_limit(url, i)
            for i, url in enumerate(image_urls)
        ]
        results = await asyncio.gather(*tasks)

        # Sort by original index to maintain order
        results.sort(key=lambda x: x[0])
        colors_batch = [colors for _, colors in results]

        return colors_batch

    async def _extract_single_image(
        self,
        image_url: str,
        max_colors: int,
        image_index: int,
    ) -> List[ColorToken]:
        """
        Extract colors from a single image

        Args:
            image_url: Image URL
            max_colors: Max colors to extract
            image_index: Index for logging

        Returns:
            List of extracted ColorToken objects
        """
        logger.info(f"Extracting colors from image {image_index + 1}: {image_url}")

        colors = await self.extractor.extract_colors_from_url(
            image_url,
            max_colors=max_colors,
        )

        logger.info(
            f"Extracted {len(colors)} colors from image {image_index + 1}"
        )
        return colors

    async def persist_aggregated_library(
        self,
        db: AsyncSession,
        library_id: int,
        project_id: int,
        aggregated_tokens: List,
        statistics: dict,
    ) -> int:
        """
        Persist aggregated tokens to database

        Args:
            db: Database session
            library_id: TokenLibrary ID to associate tokens with
            project_id: Project ID for audit trail
            aggregated_tokens: Aggregated token objects
            statistics: Aggregation statistics

        Returns:
            Count of persisted tokens
        """
        logger.info(f"Persisting {len(aggregated_tokens)} aggregated tokens")

        # Prepare database records
        token_records = []
        for token in aggregated_tokens:
            import json
            record = {
                "project_id": project_id,
                "library_id": library_id,
                "hex": token.hex,
                "rgb": token.rgb,
                "name": token.name,
                "confidence": token.confidence,
                "harmony": token.harmony,
                "temperature": token.temperature,
                "role": token.role,
                "provenance": json.dumps(token.provenance),
            }
            token_records.append(record)

        # Insert in batches (avoid DB limit issues)
        batch_size = 100
        for i in range(0, len(token_records), batch_size):
            batch = token_records[i : i + batch_size]
            await db.execute(insert(DBColorToken).values(batch))

        await db.commit()
        logger.info(f"Persisted {len(token_records)} tokens to database")
        return len(token_records)
