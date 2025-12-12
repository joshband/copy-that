"""Multi-Extractor Orchestrator for parallel spacing extraction

Runs multiple spacing extractors in parallel and aggregates results with:
- Pixel-distance deduplication
- Confidence-weighted merging
- Provenance tracking
- Graceful degradation if extractors fail
"""

import asyncio
import logging
import time
from dataclasses import dataclass

from .base import ExtractionResult, SpacingExtractorProtocol
from .models import SpacingToken

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of multi-extractor orchestration"""

    aggregated_tokens: list[SpacingToken]  # Deduplicated tokens with provenance
    extraction_results: list[ExtractionResult]
    failed_extractors: list[tuple[str, str]]  # (name, error_message)
    total_time_ms: float
    overall_confidence: float


class SpacingAggregator:
    """Aggregates spacing tokens from multiple extractors with deduplication"""

    def __init__(self, pixel_distance_threshold: float = 4.0):
        """
        Initialize aggregator

        Args:
            pixel_distance_threshold: Max pixel distance to consider tokens duplicates
        """
        self.pixel_distance_threshold = pixel_distance_threshold

    def aggregate_tokens(self, tokens_by_extractor: list[list[SpacingToken]]) -> list[SpacingToken]:
        """
        Aggregate spacing tokens from multiple extractors.

        Deduplicates tokens that are within pixel_distance_threshold of each other,
        keeping the one with highest confidence.

        Args:
            tokens_by_extractor: List of token lists, one per extractor

        Returns:
            Deduplicated list of spacing tokens with provenance metadata
        """
        if not tokens_by_extractor:
            return []

        # Flatten all tokens with provenance tracking
        all_tokens = []
        for extractor_idx, tokens in enumerate(tokens_by_extractor):
            for token in tokens:
                # Add provenance metadata
                if token.extraction_metadata is None:
                    token.extraction_metadata = {}
                token.extraction_metadata["extractor_index"] = extractor_idx
                all_tokens.append(token)

        if not all_tokens:
            return []

        # Sort by confidence (highest first) for better deduplication
        all_tokens.sort(key=lambda t: t.confidence, reverse=True)

        # Deduplicate using pixel distance
        deduplicated: list[SpacingToken] = []
        for token in all_tokens:
            # Check if this token is similar to any already deduplicated token
            is_duplicate = False
            for existing in deduplicated:
                if abs(token.value_px - existing.value_px) <= self.pixel_distance_threshold:
                    # Merge provenance if it's a duplicate
                    if existing.extraction_metadata is not None:
                        if "extractor_sources" not in existing.extraction_metadata:
                            existing.extraction_metadata["extractor_sources"] = []
                        existing.extraction_metadata["extractor_sources"].append(
                            token.extraction_metadata.get("extractor_index")
                            if token.extraction_metadata
                            else None
                        )
                    # Boost confidence for duplicates found by multiple extractors
                    existing.confidence = min(1.0, existing.confidence + token.confidence * 0.1)
                    is_duplicate = True
                    break

            if not is_duplicate:
                # Initialize extractor_sources list
                if token.extraction_metadata is not None:
                    if "extractor_sources" not in token.extraction_metadata:
                        token.extraction_metadata["extractor_sources"] = []
                    token.extraction_metadata["extractor_sources"].append(
                        token.extraction_metadata.get("extractor_index")
                    )
                deduplicated.append(token)

        return deduplicated


class SpacingExtractionOrchestrator:
    """Run multiple spacing extractors in parallel and aggregate results"""

    def __init__(
        self,
        extractors: list[SpacingExtractorProtocol],
        aggregator: SpacingAggregator | None = None,
        max_concurrent: int = 4,
    ):
        """
        Initialize orchestrator

        Args:
            extractors: List of extractors implementing SpacingExtractorProtocol
            aggregator: SpacingAggregator for deduplication (default: 4px threshold)
            max_concurrent: Max concurrent extractions (limit resource usage)
        """
        self.extractors = extractors
        self.aggregator = aggregator or SpacingAggregator(pixel_distance_threshold=4.0)
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
            if isinstance(result, BaseException):
                extractor_name = self.extractors[i].name
                failed_extractors.append((extractor_name, str(result)))
                logger.warning(f"Extractor {extractor_name} failed: {result}", exc_info=result)
            elif isinstance(result, ExtractionResult):
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
        extractor: SpacingExtractorProtocol,
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
