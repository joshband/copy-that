"""Multi-Extractor Orchestrator for parallel color extraction

Runs multiple color extractors in parallel and aggregates results with:
- Delta-E deduplication
- Confidence-weighted merging
- Provenance tracking
- Graceful degradation if extractors fail
"""

import asyncio
import logging
import time
from dataclasses import dataclass

from copy_that.extractors.color.base import ColorExtractorProtocol, ExtractionResult
from copy_that.tokens.color.aggregator import ColorAggregator, TokenLibrary

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of multi-extractor orchestration"""

    library: TokenLibrary
    extraction_results: list[ExtractionResult]
    failed_extractors: list[tuple[str, str]]  # (name, error_message)
    total_time_ms: float


class MultiExtractorOrchestrator:
    """Run multiple color extractors in parallel and aggregate results"""

    def __init__(
        self,
        extractors: list[ColorExtractorProtocol],
        aggregator: ColorAggregator,
        max_concurrent: int = 4,
    ):
        """
        Initialize orchestrator

        Args:
            extractors: List of extractors implementing ColorExtractorProtocol
            aggregator: ColorAggregator for deduplication and aggregation
            max_concurrent: Max concurrent extractions (limit resource usage)
        """
        self.extractors = extractors
        self.aggregator = aggregator
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
            OrchestrationResult with aggregated library and metadata
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

        # 3. Aggregate colors from successful extractors
        for result in successful_results:
            for color in result.colors:
                # Track which extractor(s) found each color
                self.aggregator.add_color(
                    color,
                    image_id=f"{image_id}_{result.extractor_name}",
                )

        # 4. Get deduplicated library
        library = self.aggregator.get_library()

        total_time_ms = (time.time() - start_time) * 1000

        return OrchestrationResult(
            library=library,
            extraction_results=successful_results,
            failed_extractors=failed_extractors,
            total_time_ms=total_time_ms,
        )

    async def _extract_with_error_handling(
        self,
        extractor: ColorExtractorProtocol,
        image_data: bytes,
        semaphore: asyncio.Semaphore,
    ) -> ExtractionResult:
        """Run extractor with error handling and concurrency control"""
        async with semaphore:
            try:
                return await extractor.extract(image_data)
            except Exception as e:
                # Wrap in ExtractionResult with empty colors for consistent handling
                raise RuntimeError(f"Extraction failed for {extractor.name}: {str(e)}") from e

    async def extract_all_safe(
        self,
        image_data: bytes,
        image_id: str,
    ) -> OrchestrationResult:
        """
        Safe version of extract_all that guarantees no exceptions

        Even if all extractors fail, returns an empty TokenLibrary
        """
        try:
            return await self.extract_all(image_data, image_id)
        except Exception as e:
            logger.error(f"Orchestration failed completely: {e}", exc_info=e)
            # Return empty result
            return OrchestrationResult(
                library=self.aggregator.get_library(),
                extraction_results=[],
                failed_extractors=[(extractor.name, str(e)) for extractor in self.extractors],
                total_time_ms=0,
            )
