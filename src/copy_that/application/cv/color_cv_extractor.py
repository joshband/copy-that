"""
Lightweight CV-first color extractor using Pillow + coloraide.

Goal: fast local palette for immediate UI render, later refined by AI.
"""

from __future__ import annotations

import io
from collections import Counter
from collections import Counter as CounterType
from typing import Any, cast

from coloraide import Color
from PIL import Image

from copy_that.application.color_extractor import ColorExtractionResult, ExtractedColorToken


class CVColorExtractor:
    """Quick palette extraction without remote AI."""

    def __init__(self, max_colors: int = 8):
        self.max_colors = max_colors

    def extract_from_bytes(self, data: bytes) -> ColorExtractionResult:
        image = Image.open(io.BytesIO(data)).convert("RGB")
        # Quantize to palette for speed
        image_module = cast(Any, Image)
        palette_arg: Any = getattr(image_module, "ADAPTIVE", None)
        paletted = image.convert("P", palette=palette_arg, colors=min(self.max_colors * 2, 24))
        palette = paletted.getpalette()
        if palette is None:
            return self._empty()
        raw_counts = paletted.getcolors()
        color_counts: list[tuple[int, int]] = []
        if raw_counts:
            for count, idx in raw_counts:
                if isinstance(idx, tuple):
                    # Non-palette values include actual RGB tuples; skip them.
                    continue
                color_counts.append((int(count), int(idx)))
        if not color_counts:
            return self._empty()

        # Map palette index to RGB
        def idx_to_rgb(idx: int) -> tuple[int, int, int]:
            base = idx * 3
            return palette[base], palette[base + 1], palette[base + 2]

        rgb_counts: CounterType[tuple[int, int, int]] = Counter()
        for count, idx in color_counts:
            rgb_counts[idx_to_rgb(idx)] += count

        top = rgb_counts.most_common(self.max_colors)
        tokens: list[ExtractedColorToken] = []
        total = sum(rgb_counts.values()) or 1
        for rgb, count in top:
            hex_val = "#{:02x}{:02x}{:02x}".format(*rgb)
            c = Color(hex_val)
            name = c.to("css3").to_string() if hasattr(c, "to") else hex_val
            prominence = round(count / total * 100, 2)
            tokens.append(
                ExtractedColorToken(
                    hex=hex_val,
                    rgb=f"rgb{rgb}",
                    hsl=c.convert("hsl").to_string() if hasattr(c, "convert") else None,
                    hsv=None,
                    name=name,
                    design_intent=None,
                    semantic_names=None,
                    category="cv",
                    confidence=0.6,
                    harmony=None,
                    temperature=None,
                    saturation_level=None,
                    lightness_level=None,
                    usage=[],
                    count=1,
                    prominence_percentage=prominence,
                    wcag_contrast_on_white=None,
                    wcag_contrast_on_black=None,
                    wcag_aa_compliant_text=None,
                    wcag_aaa_compliant_text=None,
                    wcag_aa_compliant_normal=None,
                    wcag_aaa_compliant_normal=None,
                    colorblind_safe=None,
                    tint_color=None,
                    shade_color=None,
                    tone_color=None,
                    closest_web_safe=None,
                    closest_css_named=None,
                    delta_e_to_dominant=None,
                    is_neutral=c.is_achromatic() if hasattr(c, "is_achromatic") else None,
                    kmeans_cluster_id=None,
                    sam_segmentation_mask=None,
                    clip_embeddings=None,
                    extraction_metadata={"source": "cv", "palette_count": len(top)},
                    histogram_significance=prominence / 100.0,
                )
            )

        dominant = [t.hex for t in tokens[:3]]
        return ColorExtractionResult(
            colors=tokens,
            dominant_colors=dominant,
            color_palette="CV palette",
            extraction_confidence=0.6,
            extractor_used="cv",
        )

    def extract_from_base64(self, image_base64: str) -> ColorExtractionResult:
        import base64

        data = base64.b64decode(image_base64.split(",")[1] if "," in image_base64 else image_base64)
        return self.extract_from_bytes(data)

    @staticmethod
    def _empty() -> ColorExtractionResult:
        return ColorExtractionResult(
            colors=[],
            dominant_colors=[],
            color_palette="",
            extraction_confidence=0.0,
            extractor_used="cv",
        )
