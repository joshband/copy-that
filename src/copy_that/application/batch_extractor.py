"""
Batch image extraction service - orchestrates color extraction for multiple images

Handles:
- Parallel/sequential image extraction
- Aggregation of results via ColorAggregator
- Database persistence of aggregated tokens
"""

import asyncio
import logging

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.color_extractor import AIColorExtractor
from copy_that.constants import DEFAULT_DELTA_E_THRESHOLD, DEFAULT_MAX_CONCURRENT_EXTRACTIONS
from copy_that.domain.models import ColorToken
from copy_that.interfaces.api.token_mappers import colors_to_repo
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.aggregate import simple_color_merge
from core.tokens.repository import InMemoryTokenRepository

logger = logging.getLogger(__name__)


class BatchColorExtractor:
    """Extract and aggregate colors from multiple images"""

    def __init__(self, max_concurrent: int = DEFAULT_MAX_CONCURRENT_EXTRACTIONS):
        """
        Initialize batch extractor

        Args:
            max_concurrent: Max concurrent image processing (API rate limits)
        """
        self.max_concurrent = max_concurrent
        self.extractor = AIColorExtractor()

    async def extract_batch(
        self,
        image_urls: list[str],
        max_colors: int = 10,
        delta_e_threshold: float = DEFAULT_DELTA_E_THRESHOLD,
    ) -> tuple[list[ColorToken], dict]:
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

        # Aggregate results using token graph merge
        repo = InMemoryTokenRepository()
        total_extracted = 0
        for batch_index, color_list in enumerate(colors_batch, start=1):
            total_extracted += len(color_list)
            batch_repo = colors_to_repo(color_list, namespace=f"token/color/batch/{batch_index}")
            for token in batch_repo.find_by_type("color"):
                repo.upsert_token(token)

        merged_repo = simple_color_merge(repo)
        unique_count = len(merged_repo.find_by_type("color"))
        stats = {
            "total_extracted": total_extracted,
            "unique": unique_count,
            "delta_e_threshold": delta_e_threshold,
            "design_tokens": tokens_to_w3c(merged_repo),
        }
        logger.info(
            f"Batch extraction complete: {unique_count} unique colors from {total_extracted} detections"
        )
        return merged_repo.find_by_type("color"), stats

    async def _extract_all_images(
        self,
        image_urls: list[str],
        max_colors: int,
    ) -> list[list[ColorToken]]:
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

        async def extract_with_limit(url: str, index: int) -> tuple[int, list[ColorToken]]:
            async with semaphore:
                try:
                    colors = await self._extract_single_image(url, max_colors, index)
                    return index, colors
                except Exception as e:
                    logger.error(f"Failed to extract {url}: {e}")
                    return index, []

        # Extract all images concurrently
        tasks = [extract_with_limit(url, i) for i, url in enumerate(image_urls)]
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
    ) -> list[ColorToken]:
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

        # Run sync method in thread pool to avoid blocking
        colors_result = await asyncio.to_thread(
            self.extractor.extract_colors_from_image_url,
            image_url,
            max_colors,
        )
        colors = colors_result.colors if hasattr(colors_result, "colors") else colors_result

        logger.info(f"Extracted {len(colors)} colors from image {image_index + 1}")
        return colors

    async def persist_aggregated_library(
        self,
        db: AsyncSession,
        library_id: int,
        project_id: int,
        aggregated_tokens: list,
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

            attrs = getattr(token, "attributes", {}) or {}
            record = {
                "project_id": project_id,
                "library_id": library_id,
                "hex": getattr(token, "hex", None) or attrs.get("hex") or token.value,
                "rgb": getattr(token, "rgb", None) or attrs.get("rgb"),
                "name": getattr(token, "name", None) or attrs.get("name"),
                "confidence": getattr(token, "confidence", None) or attrs.get("confidence"),
                "harmony": getattr(token, "harmony", None) or attrs.get("harmony"),
                "temperature": getattr(token, "temperature", None) or attrs.get("temperature"),
                "role": getattr(token, "role", None) or attrs.get("role"),
                "provenance": json.dumps(
                    getattr(token, "provenance", None) or attrs.get("provenance") or {}
                ),
            }
            token_records.append(record)

        # Insert in batches (avoid DB limit issues)
        batch_size = 100
        for i in range(0, len(token_records), batch_size):
            batch = token_records[i : i + batch_size]
            await db.execute(insert(ColorToken).values(batch))

        await db.commit()
        logger.info(f"Persisted {len(token_records)} tokens to database")
        return len(token_records)
