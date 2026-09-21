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
from copy_that.extractors.color.extractor import ExtractedColorToken
from copy_that.tokens.color.aggregator import ColorAggregator

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of multi-extractor orchestration"""

    aggregated_colors: list  # list[ExtractedColorToken] with provenance metadata
    extraction_results: list[ExtractionResult]
    failed_extractors: list[tuple[str, str]]  # (name, error_message)
    total_time_ms: float
    overall_confidence: float


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
            OrchestrationResult with aggregated colors and metadata
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

        # 3. Aggregate colors from successful extractors using ColorAggregator
        # Collect colors from each extractor and batch-aggregate with Delta-E deduplication
        colors_by_extractor = [result.colors for result in successful_results]
        library = ColorAggregator.aggregate_batch(
            colors_by_extractor,
            delta_e_threshold=self.aggregator.delta_e_threshold,
        )

        # Calculate overall confidence from extraction results
        overall_confidence = (
            sum(r.confidence_range[1] for r in successful_results) / len(successful_results)
            if successful_results
            else 0.0
        )

        total_time_ms = (time.time() - start_time) * 1000

        # Convert TokenLibrary tokens back to ExtractedColorToken for API response
        aggregated_colors = [
            ExtractedColorToken(
                hex=token.hex,
                rgb=token.rgb,
                name=token.name,
                confidence=token.confidence,
                harmony=token.harmony,
                temperature=token.temperature,
                saturation_level=token.saturation_level,
                lightness_level=token.lightness_level,
                semantic_names=token.semantic_names,
                extraction_metadata={
                    "extractor_sources": list(token.provenance.keys()),
                },
            )
            for token in library.tokens
        ]

        return OrchestrationResult(
            aggregated_colors=aggregated_colors,
            extraction_results=successful_results,
            failed_extractors=failed_extractors,
            total_time_ms=total_time_ms,
            overall_confidence=overall_confidence,
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

        Even if all extractors fail, returns an empty result set
        """
        try:
            return await self.extract_all(image_data, image_id)
        except Exception as e:
            logger.error(f"Orchestration failed completely: {e}", exc_info=e)
            # Return empty result
            return OrchestrationResult(
                aggregated_colors=[],
                extraction_results=[],
                failed_extractors=[(extractor.name, str(e)) for extractor in self.extractors],
                total_time_ms=0,
                overall_confidence=0.0,
            )
