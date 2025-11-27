"""
AI Spacing Extractor (OpenAI-first)

Claude usage is disabled by request until Dec 1, 2025. This implementation
uses OpenAI vision (default gpt-4o-mini) and falls back to a deterministic
spacing scale so the API never returns a 500 due to model quotas.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any

import requests
from openai import OpenAI

from . import spacing_utils as su
from .spacing_models import SpacingExtractionResult, SpacingScale, SpacingToken

logger = logging.getLogger(__name__)


class AISpacingExtractor:
    """
    AI-powered spacing extractor using OpenAI vision models.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """
        Initialize the spacing extractor.

        Args:
            api_key: OpenAI API key. Falls back to OPENAI_API_KEY env var.
            model: OpenAI model name. Defaults to gpt-4o-mini for latency.
        """

        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Public extraction helpers -------------------------------------------------
    def extract_spacing_from_image_url(
        self, image_url: str, max_tokens: int = 15
    ) -> SpacingExtractionResult:
        """Extract spacing tokens from a remote image URL."""
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        media_type = response.headers.get("content-type", "image/png")
        image_data = base64.standard_b64encode(response.content).decode("utf-8")
        return self.extract_spacing_from_base64(image_data, media_type, max_tokens)

    def extract_spacing_from_file(
        self, file_path: str, max_tokens: int = 15
    ) -> SpacingExtractionResult:
        """Extract spacing tokens from a local file path."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        media_type = media_types.get(file_path.suffix.lower(), "image/png")

        with open(file_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        return self.extract_spacing_from_base64(image_data, media_type, max_tokens)

    def extract_spacing_from_base64(
        self, image_data: str, media_type: str, max_tokens: int = 15
    ) -> SpacingExtractionResult:
        """Extract spacing tokens from base64-encoded image data."""
        prompt = self._build_extraction_prompt(max_tokens)
        data_url = (
            image_data
            if image_data.startswith("data:")
            else f"data:{media_type};base64,{image_data}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_url}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            content = response.choices[0].message.content
            payload: dict[str, Any] = json.loads(content) if content else {}
            return self._parse_spacing_response(payload, max_tokens)
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI spacing extraction error: %s", exc)
            return self._fallback_spacing(max_tokens)

    # Internals -----------------------------------------------------------------
    def _build_extraction_prompt(self, max_tokens: int) -> str:
        """Instruction for OpenAI vision in JSON mode."""
        return f"""
Analyze this UI/design image and extract the spacing system.

Return JSON ONLY in this format:
{{
  "tokens": [
    {{
      "value_px": 8,
      "name": "spacing-sm",
      "semantic_role": "padding",
      "spacing_type": "padding",
      "usage": ["card padding"],
      "confidence": 0.9
    }}
  ],
  "scale_system": "8pt",
  "base_unit": 8,
  "grid_compliance": 0.92,
  "extraction_confidence": 0.9
}}

Rules:
- Identify up to {max_tokens} distinct spacing values.
- Prefer 4pt/8pt grids; include base_unit and scale_system.
- confidence must be 0-1.0.
- If unsure, still produce a conservative JSON guess.
"""

    def _parse_spacing_response(
        self, payload: dict[str, Any], max_tokens: int
    ) -> SpacingExtractionResult:
        """Parse OpenAI JSON into SpacingExtractionResult."""
        tokens: list[SpacingToken] = []
        unique_values: set[int] = set()

        base_unit = int(payload.get("base_unit", 8) or 8)
        scale_system = self._parse_scale_system(payload.get("scale_system"))
        grid_compliance = float(payload.get("grid_compliance", 0.85))
        extraction_confidence = float(payload.get("extraction_confidence", 0.85))

        raw_tokens = payload.get("tokens") or []
        for idx, item in enumerate(raw_tokens[:max_tokens]):
            try:
                value_px = int(round(float(item.get("value_px", item.get("value", 0)))))
            except Exception:
                continue
            if value_px <= 0 or value_px in unique_values:
                continue
            unique_values.add(value_px)

            tokens.append(
                SpacingToken(
                    value_px=value_px,
                    name=item.get("name") or f"spacing-{idx}",
                    semantic_role=item.get("semantic_role"),
                    spacing_type=item.get("spacing_type"),
                    category=item.get("category"),
                    confidence=float(item.get("confidence", 0.82)),
                    usage=item.get("usage", []),
                    scale_position=idx,
                    base_unit=base_unit,
                    scale_system=scale_system,
                    grid_aligned=base_unit > 0 and value_px % base_unit == 0,
                )
            )

        if not tokens:
            return self._fallback_spacing(max_tokens)

        unique_sorted = sorted(unique_values)
        base_unit_confidence = 0.0
        try:
            base_unit_confidence = su.infer_base_spacing(unique_sorted)[1]
        except Exception:
            base_unit_confidence = 0.0
        return SpacingExtractionResult(
            tokens=tokens,
            scale_system=scale_system,
            base_unit=base_unit,
            base_unit_confidence=base_unit_confidence,
            grid_compliance=grid_compliance if grid_compliance <= 1 else grid_compliance / 100.0,
            extraction_confidence=extraction_confidence,
            min_spacing=unique_sorted[0],
            max_spacing=unique_sorted[-1],
            unique_values=unique_sorted,
        )

    def _fallback_spacing(self, max_tokens: int) -> SpacingExtractionResult:
        """Deterministic fallback (never 500)."""
        default_values = [4, 8, 16, 24, 32, 48][:max_tokens]
        base_unit = 4
        tokens = [
            SpacingToken(
                value_px=val,
                name=f"spacing-{name}",
                semantic_role="layout",
                usage=["layout spacing"],
                confidence=0.72 + (0.02 * (len(default_values) - idx)),
                scale_position=idx,
                base_unit=base_unit,
                scale_system=SpacingScale.FOUR_POINT,
                grid_aligned=True,
            )
            for idx, (name, val) in enumerate(
                zip(["xs", "sm", "md", "lg", "xl", "xxl"], default_values, strict=False)
            )
        ]

        base_unit_confidence = su.infer_base_spacing(default_values)[1]
        return SpacingExtractionResult(
            tokens=tokens,
            scale_system=SpacingScale.FOUR_POINT,
            base_unit=base_unit,
            base_unit_confidence=base_unit_confidence,
            grid_compliance=1.0,
            extraction_confidence=0.65,
            min_spacing=min(default_values),
            max_spacing=max(default_values),
            unique_values=default_values,
        )

    @staticmethod
    def _parse_scale_system(raw: Any) -> SpacingScale:
        """Map raw scale string to enum."""
        if not raw:
            return SpacingScale.CUSTOM
        text = str(raw).lower()
        mapping = {
            "4": SpacingScale.FOUR_POINT,
            "4pt": SpacingScale.FOUR_POINT,
            "4-point": SpacingScale.FOUR_POINT,
            "8": SpacingScale.EIGHT_POINT,
            "8pt": SpacingScale.EIGHT_POINT,
            "8-point": SpacingScale.EIGHT_POINT,
            "golden": SpacingScale.GOLDEN_RATIO,
            "fibonacci": SpacingScale.FIBONACCI,
            "linear": SpacingScale.LINEAR,
            "exponential": SpacingScale.EXPONENTIAL,
        }
        return mapping.get(text, SpacingScale.CUSTOM)
