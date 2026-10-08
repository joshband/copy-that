from __future__ import annotations

from enum import StrEnum

from copy_that.infrastructure.ai_models import (
    OPENAI_FAST_DEFAULT,
    OPENAI_PREMIUM_DEFAULT,
    OPENAI_VISION_DEFAULT,
)


class QualityTier(StrEnum):
    FAST = "fast"
    STANDARD = "standard"
    PREMIUM = "premium"

    @classmethod
    def from_str(cls, value: str | None) -> QualityTier:
        if not value:
            return cls.STANDARD
        try:
            return cls(value.lower())
        except ValueError:
            return cls.STANDARD


def color_model_for_quality(tier: QualityTier) -> str:
    """
    Map quality tier to OpenAI vision model.
    - fast: lower-cost/lower-latency
    - standard: default balance
    - premium: highest fidelity
    """
    if tier == QualityTier.FAST:
        return OPENAI_FAST_DEFAULT
    if tier == QualityTier.PREMIUM:
        return OPENAI_PREMIUM_DEFAULT
    return OPENAI_VISION_DEFAULT


def spacing_model_for_quality(tier: QualityTier) -> str:
    """
    Map quality tier to spacing vision model.
    """
    if tier == QualityTier.FAST:
        return OPENAI_FAST_DEFAULT
    if tier == QualityTier.PREMIUM:
        return OPENAI_PREMIUM_DEFAULT
    return OPENAI_VISION_DEFAULT
