from __future__ import annotations

from enum import Enum


class QualityTier(str, Enum):
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
        return "gpt-4o-mini"
    if tier == QualityTier.PREMIUM:
        return "gpt-4.1"
    return "gpt-4o"


def spacing_model_for_quality(tier: QualityTier) -> str:
    """
    Map quality tier to spacing vision model.
    """
    if tier == QualityTier.FAST:
        return "gpt-4o-mini"
    if tier == QualityTier.PREMIUM:
        return "gpt-4.1"
    return "gpt-4o"
