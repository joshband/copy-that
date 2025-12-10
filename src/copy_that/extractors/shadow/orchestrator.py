"""Multi-Extractor Orchestrator for parallel shadow extraction

Runs multiple shadow extractors in parallel and aggregates results with:
- Shadow property similarity deduplication (x, y, blur, spread, color)
- Confidence-weighted merging
- Provenance tracking
- Graceful degradation if extractors fail
"""

import asyncio
import logging
import math
import time
from dataclasses import dataclass

from .base import ExtractionResult, ShadowExtractorProtocol
from .extractor import ShadowStyle

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of multi-extractor orchestration"""

    aggregated_tokens: list[ShadowStyle]  # Deduplicated tokens with provenance
    extraction_results: list[ExtractionResult]
    failed_extractors: list[tuple[str, str]]  # (name, error_message)
    total_time_ms: float
    overall_confidence: float


class ShadowAggregator:
    """Aggregates shadow tokens from multiple extractors with deduplication"""

    def __init__(self, distance_threshold: float = 5.0):
        """
        Initialize aggregator

        Args:
            distance_threshold: Max Euclidean distance in (x,y,blur,spread) space to consider similar
        """
        self.distance_threshold = distance_threshold

    def _calculate_distance(self, shadow1: ShadowStyle, shadow2: ShadowStyle) -> float:
        """
        Calculate Euclidean distance between two shadows in (x, y, blur, spread) space.

        Args:
            shadow1: First shadow
            shadow2: Second shadow

        Returns:
            Euclidean distance
        """
        return math.sqrt(
            (shadow1.x - shadow2.x) ** 2
            + (shadow1.y - shadow2.y) ** 2
            + (shadow1.blur - shadow2.blur) ** 2
            + (shadow1.spread - shadow2.spread) ** 2
        )

    def _are_similar(self, shadow1: ShadowStyle, shadow2: ShadowStyle) -> bool:
        """
        Check if two shadow tokens are similar enough to be duplicates.

        Considers:
        - Color match (case-insensitive hex comparison)
        - Opacity similarity (within 0.05)
        - Distance in (x, y, blur, spread) space

        Args:
            shadow1: First shadow
            shadow2: Second shadow

        Returns:
            True if shadows are similar enough to be deduplicated
        """
        # Color must match (case-insensitive)
        if shadow1.color.lower() != shadow2.color.lower():
            return False

        # Opacity must be similar (within 0.05)
        if abs(shadow1.opacity - shadow2.opacity) > 0.05:
            return False

        # Distance in (x, y, blur, spread) space must be within threshold
        distance = self._calculate_distance(shadow1, shadow2)
        return distance <= self.distance_threshold

    def aggregate_tokens(self, tokens_by_extractor: list[list[ShadowStyle]]) -> list[ShadowStyle]:
        """
        Aggregate shadow tokens from multiple extractors.

        Deduplicates similar tokens using multi-dimensional distance.

        Args:
            tokens_by_extractor: List of token lists, one per extractor

        Returns:
            Deduplicated list of shadow tokens with provenance metadata
        """
        if not tokens_by_extractor:
            return []

        # Flatten all tokens with provenance tracking
        all_tokens = []
        for extractor_idx, tokens in enumerate(tokens_by_extractor):
            for token in tokens:
                # Add provenance metadata as a dict attribute (since ShadowStyle is a dataclass)
                # We'll store it as a custom attribute
                token_with_metadata = token
                if not hasattr(token_with_metadata, "extraction_metadata"):
                    object.__setattr__(token_with_metadata, "extraction_metadata", {})
                token_with_metadata.extraction_metadata["extractor_index"] = extractor_idx
                all_tokens.append(token_with_metadata)

        if not all_tokens:
            return []

        # Sort by distance from origin (prefer shadows closer to typical values)
        # This prioritizes more common shadow configurations
        all_tokens.sort(key=lambda t: math.sqrt(t.x**2 + t.y**2 + t.blur**2), reverse=False)

        # Deduplicate using similarity check
        deduplicated = []
        for token in all_tokens:
            # Check if this token is similar to any already deduplicated token
            is_duplicate = False
            for existing in deduplicated:
                if self._are_similar(token, existing):
                    # Merge provenance if it's a duplicate
                    if not hasattr(existing, "extraction_metadata"):
                        object.__setattr__(existing, "extraction_metadata", {})
                    if "extractor_sources" not in existing.extraction_metadata:
                        existing.extraction_metadata["extractor_sources"] = []
                    existing.extraction_metadata["extractor_sources"].append(
                        token.extraction_metadata.get("extractor_index")
                    )
                    # Note: ShadowStyle doesn't have confidence, so we don't boost it
                    is_duplicate = True
                    break

            if not is_duplicate:
                # Initialize extractor_sources list
                if not hasattr(token, "extraction_metadata"):
                    object.__setattr__(token, "extraction_metadata", {})
                if "extractor_sources" not in token.extraction_metadata:
                    token.extraction_metadata["extractor_sources"] = []
                token.extraction_metadata["extractor_sources"].append(
                    token.extraction_metadata.get("extractor_index")
                )
                deduplicated.append(token)

        return deduplicated


class ShadowExtractionOrchestrator:
    """Run multiple shadow extractors in parallel and aggregate results"""

    def __init__(
        self,
        extractors: list[ShadowExtractorProtocol],
        aggregator: ShadowAggregator | None = None,
        max_concurrent: int = 4,
    ):
        """
        Initialize orchestrator

        Args:
            extractors: List of extractors implementing ShadowExtractorProtocol
            aggregator: ShadowAggregator for deduplication (default: 5.0 distance threshold)
            max_concurrent: Max concurrent extractions (limit resource usage)
        """
        self.extractors = extractors
        self.aggregator = aggregator or ShadowAggregator(distance_threshold=5.0)
        self.max_concurrent = max_concurrent

    async def extract_all(
        self,
        image_data: bytes,
        image_id: str,
    ) -> OrchestrationResult:
        """
        Run all extractors in parallel and aggregate results

        Args:
            image_data: Raw image bytes
            image_id: Unique identifier for this image

        Returns:
            OrchestrationResult with aggregated tokens and metadata
        """
        start_time = time.time()

        # 1. Run extractors in parallel with semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        extraction_tasks = [
            self._extract_with_error_handling(extractor, image_data, semaphore)
            for extractor in self.extractors
        ]

        results = await asyncio.gather(*extraction_tasks, return_exceptions=True)

        # 2. Separate successful and failed results
        successful_results: list[ExtractionResult] = []
        failed_extractors: list[tuple[str, str]] = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                extractor_name = self.extractors[i].name
                failed_extractors.append((extractor_name, str(result)))
                logger.warning(f"Extractor {extractor_name} failed: {result}", exc_info=result)
            else:
                successful_results.append(result)

        # 3. Aggregate tokens from successful extractors
        tokens_by_extractor = [result.tokens for result in successful_results]
        aggregated_tokens = self.aggregator.aggregate_tokens(tokens_by_extractor)

        # Calculate overall confidence from extraction results
        overall_confidence = (
            sum(r.confidence_range[1] for r in successful_results) / len(successful_results)
            if successful_results
            else 0.0
        )

        total_time_ms = (time.time() - start_time) * 1000

        return OrchestrationResult(
            aggregated_tokens=aggregated_tokens,
            extraction_results=successful_results,
            failed_extractors=failed_extractors,
            total_time_ms=total_time_ms,
            overall_confidence=overall_confidence,
        )

    async def _extract_with_error_handling(
        self,
        extractor: ShadowExtractorProtocol,
        image_data: bytes,
        semaphore: asyncio.Semaphore,
    ) -> ExtractionResult:
        """Run extractor with error handling and concurrency control"""
        async with semaphore:
            try:
                return await extractor.extract(image_data)
            except Exception as e:
                raise RuntimeError(f"Extraction failed for {extractor.name}: {str(e)}") from e

    async def extract_all_safe(
        self,
        image_data: bytes,
        image_id: str,
    ) -> OrchestrationResult:
        """
        Safe version of extract_all that guarantees no exceptions

        Even if all extractors fail, returns an empty result set
        """
        try:
            return await self.extract_all(image_data, image_id)
        except Exception as e:
            logger.error(f"Orchestration failed completely: {e}", exc_info=e)
            # Return empty result
            return OrchestrationResult(
                aggregated_tokens=[],
                extraction_results=[],
                failed_extractors=[(extractor.name, str(e)) for extractor in self.extractors],
                total_time_ms=0,
                overall_confidence=0.0,
            )
