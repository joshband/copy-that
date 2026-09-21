"""
Adapter implementations for spacing extraction.

Wraps existing spacing extractors to conform to SpacingExtractorProtocol.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from typing import Any

from .base import ExtractionResult
from .cv_extractor import CVSpacingExtractor
from .models import SpacingToken

logger = logging.getLogger(__name__)


def _detect_media_type(image_data: bytes) -> str:
    if image_data.startswith(b"\x89PNG"):
        return "image/png"
    if image_data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_data.startswith(b"GIF87a") or image_data.startswith(b"GIF89a"):
        return "image/gif"
    if image_data.startswith(b"RIFF") and b"WEBP" in image_data[:20]:
        return "image/webp"
    return "image/png"


def _to_extractor_spacing_token(token: Any) -> SpacingToken:
    """Map application/CV SpacingToken → extractors.spacing.models.SpacingToken."""
    if isinstance(token, SpacingToken):
        return token
    if hasattr(token, "model_dump"):
        payload = token.model_dump()
    else:
        payload = {
            "value_px": int(getattr(token, "value_px", 0) or 0),
            "name": str(getattr(token, "name", "spacing")),
            "confidence": float(getattr(token, "confidence", 0.5) or 0.5),
            "semantic_role": getattr(token, "semantic_role", None),
            "spacing_type": getattr(token, "spacing_type", None),
            "category": getattr(token, "category", None),
            "extraction_metadata": getattr(token, "extraction_metadata", None),
            "usage": list(getattr(token, "usage", []) or []),
            "count": int(getattr(token, "count", 1) or 1),
        }
    return SpacingToken.model_validate(payload)


class CVSpacingExtractorAdapter:
    """Wraps CVSpacingExtractor for async extraction with protocol compliance"""

    def __init__(self, max_tokens: int = 10):
        """
        Initialize the CV spacing adapter.

        Args:
            max_tokens: Maximum spacing tokens to extract
        """
        self.extractor = CVSpacingExtractor(max_tokens=max_tokens)
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        """Extractor name for identification"""
        return "cv-spacing"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract spacing tokens from image data.

        Args:
            image_data: Raw image bytes

        Returns:
            ExtractionResult with tokens and metadata
        """
        start_time = time.time()

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, self.extractor.extract_from_bytes, image_data)

            raw_tokens = list(getattr(result, "tokens", []) or [])[: self.max_tokens]
            tokens = [_to_extractor_spacing_token(t) for t in raw_tokens]
            execution_time_ms = (time.time() - start_time) * 1000

            live = float(getattr(result, "extraction_confidence", 0.0) or 0.0)
            token_confs = [
                float(t.confidence) for t in tokens if getattr(t, "confidence", None) is not None
            ]
            if token_confs:
                lo = min(min(token_confs), live) if live > 0 else min(token_confs)
                hi = max(max(token_confs), live) if live > 0 else max(token_confs)
                confidence_range = (round(lo, 3), round(hi, 3))
            elif live > 0:
                confidence_range = (round(live, 3), round(live, 3))
            else:
                confidence_range = (0.15, 0.35)

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"CV spacing extraction failed: {e}")
            raise ValueError(f"Failed to extract spacing: {e}") from e


class AISpacingExtractorAdapter:
    """Wraps application AISpacingExtractor for async protocol compliance."""

    def __init__(self, max_tokens: int = 15, model: str | None = None):
        from copy_that.application.spacing_extractor import AISpacingExtractor

        self.extractor = AISpacingExtractor(model=model)
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        return "ai-spacing"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        start_time = time.time()
        b64 = base64.standard_b64encode(image_data).decode("utf-8")
        media_type = _detect_media_type(image_data)
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.extractor.extract_spacing_from_base64(
                    b64, media_type, self.max_tokens
                ),
            )
            raw_tokens = list(getattr(result, "tokens", []) or [])[: self.max_tokens]
            tokens = [_to_extractor_spacing_token(t) for t in raw_tokens]
            confs = [t.confidence for t in tokens] or [0.5]
            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=(time.time() - start_time) * 1000,
                confidence_range=(min(confs), max(confs)),
            )
        except Exception as e:
            logger.error(f"AI spacing extraction failed: {e}")
            raise ValueError(f"Failed to extract spacing: {e}") from e


# Backward compatibility aliases
CVSpacingAdapter = CVSpacingExtractorAdapter
