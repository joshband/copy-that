"""CV-based shadow extraction.

Default path (``ENABLE_DARK_BLOB_SHADOW_CV`` unset/false): classical shadowlab
cues → CSS box-shadow style tokens (subtle/medium/strong). Dark-blob morphology
is **opt-in only** — it produces high false positives on dark-mode UI chrome.

Prefer this classical synthesis (or AI enhancement) for design tokens; keep
production lighting flags off.
"""

from __future__ import annotations

import logging
import os
import re
from base64 import b64decode

import cv2
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Product-facing copy when classical path finds no elevation cues (not a hard failure).
NO_ELEVATION_DETECTED_MESSAGE = "No elevation detected"

_PX_TOKEN_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*px", re.IGNORECASE)
_RGBA_TOKEN_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([0-9.]+))?\s*\)",
    re.IGNORECASE,
)


class ExtractedShadowToken(BaseModel):
    """Shadow token extracted from UI images"""

    x_offset: float = Field(..., description="Horizontal offset in pixels")
    y_offset: float = Field(..., description="Vertical offset in pixels")
    blur_radius: float = Field(..., description="Blur radius in pixels")
    spread_radius: float = Field(default=0.0, description="Spread radius in pixels")
    color_hex: str = Field(..., description="Shadow color in hex format (e.g., #000000)")
    opacity: float = Field(..., ge=0, le=1, description="Shadow opacity 0-1")
    shadow_type: str = Field(..., description="Type: 'drop', 'inner', or 'text'")
    semantic_name: str = Field(..., description="Human-readable name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    is_inset: bool = Field(default=False, description="Is this an inset/inner shadow")
    affects_text: bool = Field(default=False, description="Does this shadow apply to text")


class ShadowExtractionResult(BaseModel):
    """Result of CV shadow extraction"""

    shadows: list[ExtractedShadowToken] = Field(default_factory=list)
    shadow_count: int = Field(default=0)
    extraction_confidence: float = Field(default=0.0)
    extractor_used: str = "cv_edge_detection"
    opacity_tokens: list[dict[str, float | str]] = Field(
        default_factory=list,
        description="Opacity values derived from shadow opacities (CSS number tokens)",
    )
    product_message: str | None = Field(
        default=None,
        description="Optional product-facing status (e.g. no elevation detected)",
    )
    warnings: list[str] = Field(default_factory=list)


def _dark_blob_cv_enabled() -> bool:
    return os.getenv("ENABLE_DARK_BLOB_SHADOW_CV", "0").lower() in {"1", "true", "yes"}


def _opacity_from_shadows(shadows: list[ExtractedShadowToken]) -> list[dict[str, float | str]]:
    """Derive unique opacity number descriptors from CSS shadow opacities."""
    seen: set[float] = set()
    out: list[dict[str, float | str]] = []
    for shadow in shadows:
        opacity = round(float(shadow.opacity), 3)
        if opacity in seen:
            continue
        seen.add(opacity)
        slug = shadow.semantic_name.replace(" ", "-").lower()
        if not slug.startswith("shadow"):
            slug = f"shadow-{slug}"
        out.append(
            {
                "id": f"opacity.{slug}",
                "value": opacity,
                "source": "shadow",
                "shadow_name": shadow.semantic_name,
            }
        )
    return out


def _first_shadow_layer(css: str) -> str:
    """Return the first box-shadow layer, ignoring commas inside rgba(...)."""
    depth = 0
    for index, char in enumerate(css):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            return css[:index].strip()
    return css.strip()


def _parse_css_layer(css: str, role: str, confidence: float) -> ExtractedShadowToken | None:
    """Parse first box-shadow layer into an ExtractedShadowToken."""
    primary = _first_shadow_layer(css)
    color_match = _RGBA_TOKEN_RE.search(primary)
    if color_match is None:
        return None

    r = int(color_match.group(1))
    g = int(color_match.group(2))
    b = int(color_match.group(3))
    raw_opacity = color_match.group(4)
    opacity = float(raw_opacity) if raw_opacity is not None else 1.0
    length_part = primary[: color_match.start()] + primary[color_match.end() :]
    nums = [float(match.group(1)) for match in _PX_TOKEN_RE.finditer(length_part)]
    if len(nums) < 2:
        return None

    return ExtractedShadowToken(
        x_offset=nums[0],
        y_offset=nums[1],
        blur_radius=nums[2] if len(nums) > 2 else 0.0,
        spread_radius=nums[3] if len(nums) > 3 else 0.0,
        color_hex=f"#{r:02x}{g:02x}{b:02x}",
        opacity=max(0.0, min(1.0, opacity)),
        shadow_type="drop",
        semantic_name=f"shadow-{role}",
        confidence=confidence,
        is_inset=False,
        affects_text=False,
    )


def _roles_for_density(density: str, area: float) -> tuple[str, ...]:
    """Map classical density/area to CSS elevation roles (avoid over-claiming)."""
    if density == "sparse" or area < 0.08:
        return ("subtle",)
    if density == "moderate" or area < 0.25:
        return ("subtle", "medium")
    return ("subtle", "medium", "strong")


def _synthesize_classical_css_tokens(image_bgr: np.ndarray) -> ShadowExtractionResult:
    """Classical shadowlab cues → CSS elevation tokens (no dark-blob)."""
    from copy_that.shadowlab.integration import ShadowTokenIntegration
    from copy_that.shadowlab.tokens import analyze_image_for_shadows

    analysis = analyze_image_for_shadows(image_bgr, use_geometry=False)
    features = analysis.get("features") or {}
    tokens_meta = analysis.get("tokens") or {}
    area = float(features.get("shadow_area_fraction") or 0.0)
    conf = float(tokens_meta.get("extraction_confidence") or 0.0)
    density = str(tokens_meta.get("style_density") or "moderate")
    # Flat / no-cue images: do not invent elevation claims
    if area < 0.002 or conf < 0.12:
        return ShadowExtractionResult(
            shadow_count=0,
            extraction_confidence=0.0,
            extractor_used="cv_classical_empty",
            product_message=NO_ELEVATION_DETECTED_MESSAGE,
            warnings=[NO_ELEVATION_DETECTED_MESSAGE],
        )

    css = ShadowTokenIntegration.suggest_css_box_shadow(analysis)
    # Classical conf already blends area/softness/contrast; keep role clamps honest.
    base_conf = max(0.35, min(0.8, conf if conf > 0 else 0.45 + min(area, 0.2)))
    role_conf = {"subtle": base_conf, "medium": base_conf * 0.95, "strong": base_conf * 0.9}
    shadows: list[ExtractedShadowToken] = []
    for role in _roles_for_density(density, area):
        layer = css.get(role)
        if not isinstance(layer, str):
            continue
        parsed = _parse_css_layer(layer, role, role_conf[role])
        if parsed:
            shadows.append(parsed)

    if not shadows:
        return ShadowExtractionResult(
            shadow_count=0,
            extraction_confidence=0.0,
            extractor_used="cv_classical_empty",
            product_message=NO_ELEVATION_DETECTED_MESSAGE,
            warnings=[NO_ELEVATION_DETECTED_MESSAGE],
        )

    avg = sum(s.confidence for s in shadows) / len(shadows)
    return ShadowExtractionResult(
        shadows=shadows,
        shadow_count=len(shadows),
        extraction_confidence=avg,
        extractor_used="cv_classical_css",
        opacity_tokens=_opacity_from_shadows(shadows),
    )


class CVShadowExtractor:
    """Shadow CV: classical CSS synthesis by default; dark-blob opt-in."""

    def __init__(self):
        self.min_shadow_area = 10  # Minimum pixels for shadow candidate
        self.blur_kernel = (5, 5)
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def extract_shadows(
        self,
        base64_image: str = "",
        media_type: str = "image/png",
    ) -> ShadowExtractionResult:
        """Extract shadow CSS tokens via classical cues, or dark-blob when opted in."""
        _ = media_type
        if not base64_image:
            logger.warning("No image provided to CV shadow extractor")
            return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

        try:
            image_data = b64decode(base64_image)
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

            if image is None:
                logger.warning("Failed to decode image")
                return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

            if _dark_blob_cv_enabled():
                return self._detect_shadows_dark_blob(image)

            try:
                return _synthesize_classical_css_tokens(image)
            except Exception as exc:
                logger.warning("Classical shadow CSS synthesis failed: %s", exc)
                return ShadowExtractionResult(
                    shadow_count=0,
                    extraction_confidence=0.0,
                    extractor_used="cv_classical_failed",
                )

        except Exception as e:
            logger.exception("CV shadow extraction failed: %s", e)
            return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

    def _detect_shadows_dark_blob(self, image: np.ndarray) -> ShadowExtractionResult:
        """Legacy dark-region morphology (opt-in only)."""
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        _, dark_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, self.morph_kernel, iterations=1)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, self.morph_kernel, iterations=1)

        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shadows: list[ExtractedShadowToken] = []
        total_confidence = 0.0
        image_area = float(max(height * width, 1))

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_shadow_area:
                continue
            # Reject large dark panels / nav chrome (common dark-mode FPs)
            if area / image_area > 0.12:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            edge_margin = 5
            if (
                x < edge_margin
                or y < edge_margin
                or x + w > width - edge_margin
                or y + h > height - edge_margin
            ):
                continue

            roi = gray[y : y + h, x : x + w]
            if roi.size == 0:
                continue
            # Prefer soft penumbra: high local variance; reject flat fills
            roi_std = float(np.std(roi))
            if roi_std < 8.0:
                continue

            avg_darkness = float(np.mean(255 - roi) / 255.0)
            shadow = ExtractedShadowToken(
                x_offset=float(x),
                y_offset=float(y),
                blur_radius=max(1.0, roi_std / 25.0),
                spread_radius=0.0,
                color_hex="#000000",
                opacity=min(1.0, avg_darkness),
                shadow_type="drop",
                semantic_name=f"shadow-{len(shadows) + 1}",
                confidence=max(0.2, min(0.55, avg_darkness * 0.5)),
                is_inset=False,
                affects_text=False,
            )
            shadows.append(shadow)
            total_confidence += shadow.confidence

        avg_confidence = total_confidence / len(shadows) if shadows else 0.0
        return ShadowExtractionResult(
            shadows=shadows,
            shadow_count=len(shadows),
            extraction_confidence=avg_confidence,
            extractor_used="cv_dark_blob_opt_in",
            opacity_tokens=_opacity_from_shadows(shadows),
        )
