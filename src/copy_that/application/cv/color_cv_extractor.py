"""
Lightweight CV-first color extractor using Pillow + coloraide.

Goal: fast local palette for immediate UI render, later refined by AI.
"""

from __future__ import annotations

from collections import Counter
from collections import Counter as CounterType
from typing import TYPE_CHECKING, Any, cast

import numpy as np
from coloraide import Color
from PIL import Image

from copy_that.application import color_utils
from copy_that.application.color_extractor import ColorExtractionResult, ExtractedColorToken
from copy_that.application.cv.debug_color import generate_debug_overlay
from core.tokens.color import make_color_token
from core.tokens.graph import TokenGraph
from core.tokens.model import TokenType
from core.tokens.repository import TokenRepository
from cv_pipeline.preprocess import preprocess_image

if TYPE_CHECKING:
    pass


class CVColorExtractor:
    """Quick palette extraction without remote AI."""

    def __init__(self, max_colors: int = 8, use_superpixels: bool = True):
        self.max_colors = max_colors
        self.use_superpixels = use_superpixels

    def extract_from_bytes(
        self,
        data: bytes,
        *,
        token_repo: TokenRepository | None = None,
        token_namespace: str = "token/color/cv",
    ) -> ColorExtractionResult:
        views = preprocess_image(data)
        image = views["pil_image"]
        # Superpixel palette (preferred) -> fallback to palette quantization
        image_module = cast(Any, Image)
        rgb_counts: CounterType[tuple[int, int, int]] = Counter()

        super_pixels = self._superpixel_palette(views["cv_bgr"]) if self.use_superpixels else []
        if super_pixels:
            for rgb, cnt in super_pixels:
                key: tuple[int, int, int] = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
                rgb_counts[key] += int(cnt)
        else:
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

            for count, idx in color_counts:
                rgb_counts[idx_to_rgb(idx)] += count

        # Use a tighter cap when superpixels are available; they already smooth noise.
        top_count = self.max_colors if self.use_superpixels else self.max_colors * 2
        top = rgb_counts.most_common(top_count)
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

        # Cluster similar CV colors to reduce near-duplicates
        cluster_threshold = 1.5 if self.use_superpixels else 2.0
        tokens = cast(
            list[ExtractedColorToken],
            color_utils.cluster_color_tokens(tokens, threshold=cluster_threshold),
        )
        # Keep most prominent tokens to reduce noise
        tokens = sorted(tokens, key=lambda t: t.prominence_percentage or 0, reverse=True)[
            : self.max_colors
        ]
        bg_hex = self._detect_background_hex(image, tokens) or None
        backgrounds = [bg_hex] if bg_hex else color_utils.assign_background_roles(tokens)
        if bg_hex:
            # Tag the closest token and move it to the front
            best = None
            best_delta = 1e9
            for tok in tokens:
                try:
                    d = color_utils.delta_oklch(tok.hex, bg_hex)
                    if d < best_delta:
                        best_delta = d
                        best = tok
                except Exception:
                    continue
            if best:
                best.background_role = "primary"
                # Move background token to front
                tokens = [best] + [t for t in tokens if t is not best]
                # Drop duplicates of same hex if any
                seen_hex = set()
                deduped = []
                for t in tokens:
                    hx = getattr(t, "hex", "").lower()
                    if hx in seen_hex and hx == bg_hex.lower():
                        continue
                    seen_hex.add(hx)
                    deduped.append(t)
                tokens = deduped

        primary_bg = backgrounds[0] if backgrounds else None
        color_utils.apply_contrast_categories(tokens, primary_bg)
        color_utils.tag_foreground_colors(tokens, primary_bg)
        color_utils.assign_text_roles(tokens, primary_bg)
        accent_obj = color_utils.select_accent_token(tokens, primary_bg)
        if isinstance(accent_obj, ExtractedColorToken):
            accent_obj.foreground_role = accent_obj.foreground_role or "accent"
            accent_obj.extraction_metadata = {
                **(accent_obj.extraction_metadata or {}),
                "accent": True,
            }
            tokens.extend(
                cast(list[ExtractedColorToken], color_utils.create_state_variants(accent_obj))
            )

        dominant = [t.hex for t in tokens[:3]]
        segmented_palette = self._segment_palette(views.get("cv_bgr"))
        debug_overlay = generate_debug_overlay(
            views["cv_bgr"],
            background_hex=bg_hex,
            text_hexes=[t.hex for t in tokens if (t.extraction_metadata or {}).get("text_role")],
            palette_hexes=[t.hex for t in tokens[: self.max_colors]],
        )
        debug_payload: dict[str, Any] = {}
        if debug_overlay:
            debug_payload["overlay_png_base64"] = debug_overlay
        if segmented_palette:
            debug_payload["segmented_palette"] = segmented_palette
        result = ColorExtractionResult(
            colors=tokens,
            dominant_colors=dominant,
            color_palette="CV palette",
            extraction_confidence=0.6,
            extractor_used="cv",
            background_colors=backgrounds,
            debug=debug_payload or None,
        )
        if token_repo:
            graph = TokenGraph(token_repo)
            self._store_tokens(tokens, graph, token_namespace)
        return result

    def extract_from_base64(
        self,
        image_base64: str,
        *,
        token_repo: TokenRepository | None = None,
        token_namespace: str = "token/color/cv",
    ) -> ColorExtractionResult:
        import base64

        data = base64.b64decode(image_base64.split(",")[1] if "," in image_base64 else image_base64)
        return self.extract_from_bytes(
            data,
            token_repo=token_repo,
            token_namespace=token_namespace,
        )

    @staticmethod
    def _empty() -> ColorExtractionResult:
        return ColorExtractionResult(
            colors=[],
            dominant_colors=[],
            color_palette="",
            extraction_confidence=0.0,
            extractor_used="cv",
        )

    @staticmethod
    def _store_tokens(
        tokens: list[ExtractedColorToken],
        token_graph: TokenGraph,
        token_namespace: str,
    ) -> None:
        namespace = token_namespace.rstrip("/")
        for index, source in enumerate(tokens, start=1):
            token_id = f"{namespace}/{index:02d}"
            color = Color(source.hex)
            attributes = {
                "hex": source.hex,
                "rgb": source.rgb,
                "name": source.name,
                "confidence": source.confidence,
                "category": source.category,
                "source": source.extraction_metadata.get("source")
                if source.extraction_metadata
                else "cv",
            }
            # Include optional descriptors if present
            optional_fields = [
                "hsl",
                "hsv",
                "design_intent",
                "semantic_names",
                "harmony",
                "temperature",
                "saturation_level",
                "lightness_level",
                "usage",
                "prominence_percentage",
                "foreground_role",
                "background_role",
            ]
            for field_name in optional_fields:
                value = getattr(source, field_name, None)
                if value:
                    attributes[field_name] = value

            token = make_color_token(token_id, color, attributes)
            token_graph.add_token(token)

            # Alias role tokens to palette ids
            bg_role = getattr(source, "background_role", None)
            if bg_role:
                alias_id = f"{namespace}/background.{bg_role}"
                token_graph.add_alias(
                    alias_id,
                    token_id,
                    TokenType.COLOR,
                    role="background",
                    background_role=bg_role,
                )
            fg_role = getattr(source, "foreground_role", None)
            if fg_role:
                alias_id = f"{namespace}/text.{fg_role}"
                token_graph.add_alias(
                    alias_id,
                    token_id,
                    TokenType.COLOR,
                    role="text",
                    foreground_role=fg_role,
                )
            if (source.extraction_metadata or {}).get("accent"):
                alias_id = f"{namespace}/accent.primary"
                token_graph.add_alias(
                    alias_id,
                    token_id,
                    TokenType.COLOR,
                    role="accent",
                )

    @staticmethod
    def _detect_background_hex(image: Image.Image, tokens: list[ExtractedColorToken]) -> str | None:
        """Detect dominant background via corner/edge sampling and map to nearest token."""
        try:
            rgb = image.convert("RGB")
            w, h = rgb.size
            patch = max(4, min(w, h) // 12)
            samples = []
            coords = [
                (0, 0),
                (w - patch, 0),
                (0, h - patch),
                (w - patch, h - patch),
                (w // 2 - patch // 2, 0),
                (w // 2 - patch // 2, h - patch),
            ]
            for x, y in coords:
                for i in range(patch):
                    for j in range(patch):
                        samples.append(rgb.getpixel((min(w - 1, x + i), min(h - 1, y + j))))
            if not samples:
                return None
            hex_counts = Counter(
                f"#{r:02x}{g:02x}{b:02x}"
                for sample in samples
                if isinstance(sample, tuple) and len(sample) == 3
                for r, g, b in [sample]
            )
            bg_hex, _ = hex_counts.most_common(1)[0]
            # Map to nearest token by OKLCH
            best = None
            best_delta = 1e9
            for tok in tokens:
                try:
                    d = color_utils.delta_oklch(tok.hex, bg_hex)
                    if d < best_delta:
                        best_delta = d
                        best = tok.hex
                except Exception:
                    continue
            return best or bg_hex
        except Exception:
            return None

    @staticmethod
    def _segment_palette(cv_bgr: Any, k: int = 8) -> list[dict[str, Any]]:
        """
        Lightweight segmentation using k-means to surface dominant regions and coverage.
        Returns a list of dicts with hex and coverage percentage.
        """
        if cv_bgr is None:
            return []
        try:
            import cv2  # type: ignore[import-not-found]

            data = np.reshape(cv_bgr, (-1, 3)).astype(np.float32)
            k = max(2, min(k, 12))
            criteria: tuple[int, int, float] = (
                cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                10,
                1.0,
            )
            # bestLabels can be empty when seeding with k-means++
            best_labels = np.empty((0, 1), dtype=np.float32)
            _, labels, centers = cast(
                tuple[int, np.ndarray[Any, Any], np.ndarray[Any, Any]],
                cv2.kmeans(
                    data,
                    k,
                    best_labels,
                    criteria,
                    3,
                    cv2.KMEANS_PP_CENTERS,
                ),  # type: ignore[name-defined]
            )
            counts = np.bincount(labels.flatten(), minlength=k)
            total = float(np.sum(counts)) or 1.0
            palette: list[dict[str, Any]] = []
            for center, count in zip(centers, counts, strict=False):
                r, g, b = [int(round(v)) for v in center]
                hex_val = f"#{r:02x}{g:02x}{b:02x}"
                palette.append(
                    {
                        "hex": hex_val,
                        "coverage": round((float(count) / total) * 100.0, 2),
                    }
                )
            # Sort by coverage descending
            palette.sort(key=lambda p: p["coverage"], reverse=True)
            return palette
        except Exception:
            return []

    @staticmethod
    def _superpixel_palette(cv_bgr: Any) -> list[tuple[tuple[int, int, int], int]]:
        """Return list of (rgb, count) from superpixels; fallback empty if unavailable."""
        try:
            from skimage import segmentation  # type: ignore[import-not-found]
        except Exception:
            return []
        try:
            rgb = cv_bgr[:, :, ::-1]  # BGR->RGB
            labels = segmentation.slic(
                rgb,
                n_segments=120,
                compactness=20,
                start_label=0,
            )
            unique, counts = np.unique(labels, return_counts=True)
            colors: list[tuple[tuple[int, int, int], int]] = []
            for lbl, cnt in zip(unique, counts, strict=False):
                mask = labels == lbl
                mean_rgb = rgb[mask].mean(axis=0)
                colors.append(
                    (
                        (
                            int(round(mean_rgb[0])),
                            int(round(mean_rgb[1])),
                            int(round(mean_rgb[2])),
                        ),
                        int(cnt),
                    )
                )
            return colors
        except Exception:
            return []
