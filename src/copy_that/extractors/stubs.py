"""Stub extractors for DTCG types without a live image or derive pipeline yet."""

from __future__ import annotations

from typing import Any

from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.dtcg_capability import CoverageStatus, capability_for


class StubDtcgExtractor(BaseExtractor):
    """Registry placeholder: returns no tokens until a real extractor ships."""

    def __init__(self, token_type: str) -> None:
        self.token_type = token_type
        cap = capability_for(token_type)
        self.coverage_status = cap.status if cap else CoverageStatus.STUB

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        return []


class DurationStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("duration")


class CubicBezierStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("cubicBezier")


class NumberStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("number")


class StrokeStyleStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("strokeStyle")


class TransitionStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("transition")


class GradientStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("gradient")


# Phase 1 stubs retained for import compatibility; registry uses derive extractors.
class DimensionStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("dimension")


class FontFamilyStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("fontFamily")


class FontWeightStubExtractor(StubDtcgExtractor):
    def __init__(self) -> None:
        super().__init__("fontWeight")
