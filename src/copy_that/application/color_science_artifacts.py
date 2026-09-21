from __future__ import annotations

import base64
from collections.abc import Sequence
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import coloraide
from PIL import Image, ImageDraw

from copy_that.application import color_utils
from copy_that.extractors.cv_helpers.debug_color import generate_palette_histogram, generate_palette_strip
from copy_that.application.semantic_color_naming import analyze_color


@dataclass(frozen=True)
class ColorScienceArtifacts:
    images: list[dict[str, Any]]
    json: list[dict[str, Any]]


def _encode_png(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _select_palette_colors(
    colors: Sequence[Any],
    *,
    max_colors: int,
    exclude_state_variants: bool = True,
) -> list[Any]:
    selected: list[Any] = []
    seen: set[str] = set()
    for color in colors:
        meta = getattr(color, "extraction_metadata", None) or {}
        if exclude_state_variants and isinstance(meta, dict) and meta.get("state_role"):
            continue
        hex_val = getattr(color, "hex", None) or getattr(color, "value", None)
        if not hex_val:
            continue
        normalized = color_utils.normalize_hex(str(hex_val))
        if normalized in seen:
            continue
        seen.add(normalized)
        selected.append(color)
        if len(selected) >= max_colors:
            break
    return selected


def _normalize_hexes(colors: Sequence[Any]) -> list[str]:
    return [
        color_utils.normalize_hex(str(getattr(color, "hex", None) or getattr(color, "value", None)))
        for color in colors
        if getattr(color, "hex", None) or getattr(color, "value", None)
    ]


def _palette_weights(colors: Sequence[Any], max_colors: int) -> list[float]:
    weights: list[float] = []
    for color in colors[:max_colors]:
        weight = getattr(color, "prominence_percentage", None)
        if weight is None:
            weight = 0.0
        weights.append(float(weight))
    if any(weights):
        return weights
    if not colors:
        return []
    return [round(100.0 / len(colors), 2) for _ in colors[:max_colors]]


def _build_metrics(hexes: list[str]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for hex_val in hexes:
        oklch = coloraide.Color(hex_val).convert("oklch")
        l, c_val, h = oklch.coords()
        harmony_data = color_utils.get_color_harmony_advanced(hex_val, hexes, return_metadata=True)
        if not isinstance(harmony_data, dict):
            harmony_data = {"harmony": harmony_data, "confidence": None}
        metrics.append(
            {
                "hex": hex_val,
                "hsl": color_utils.hex_to_hsl(hex_val),
                "hsv": color_utils.hex_to_hsv(hex_val),
                "oklch": {
                    "l": round(float(l), 4),
                    "c": round(float(c_val), 4),
                    "h": round(float(h), 2),
                },
                "temperature": color_utils.get_color_temperature(hex_val),
                "saturation_level": color_utils.get_saturation_level(hex_val),
                "lightness_level": color_utils.get_lightness_level(hex_val),
                "relative_luminance": round(color_utils.relative_luminance(hex_val), 4),
                "is_neutral": color_utils.is_neutral_color(hex_val),
                "in_gamut": color_utils.is_color_in_gamut(hex_val),
                "semantic_names": analyze_color(hex_val),
                "harmony": harmony_data,
            }
        )
    return metrics


def _delta_e_matrix(hexes: list[str]) -> list[list[float]]:
    matrix: list[list[float]] = []
    for hx in hexes:
        row = []
        for other in hexes:
            row.append(round(color_utils.calculate_delta_e(hx, other), 3))
        matrix.append(row)
    return matrix


def _contrast_matrix(hexes: list[str]) -> list[list[float]]:
    matrix: list[list[float]] = []
    for hx in hexes:
        row = []
        for other in hexes:
            row.append(round(color_utils.contrast_ratio(hx, other), 3))
        matrix.append(row)
    return matrix


def _heat_color(
    value: float,
    vmin: float,
    vmax: float,
    low: tuple[int, int, int],
    high: tuple[int, int, int],
) -> tuple[int, int, int]:
    if vmax <= vmin:
        return low
    t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    return (
        int(low[0] + (high[0] - low[0]) * t),
        int(low[1] + (high[1] - low[1]) * t),
        int(low[2] + (high[2] - low[2]) * t),
    )


def _render_heatmap(
    hexes: list[str],
    matrix: list[list[float]],
    *,
    low: tuple[int, int, int],
    high: tuple[int, int, int],
) -> str | None:
    if not hexes or not matrix:
        return None
    n = len(hexes)
    cell = 24
    label = 16
    pad = 12
    width = pad * 2 + label + n * cell
    height = pad * 2 + label + n * cell
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    vmin = min(min(row) for row in matrix)
    vmax = max(max(row) for row in matrix)
    origin_x = pad + label
    origin_y = pad + label

    for i, hx in enumerate(hexes):
        x0 = origin_x + i * cell
        y0 = pad
        draw.rectangle((x0, y0, x0 + cell, y0 + label), fill=hx, outline=(0, 0, 0))
        x1 = pad
        y1 = origin_y + i * cell
        draw.rectangle((x1, y1, x1 + label, y1 + cell), fill=hx, outline=(0, 0, 0))

    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            x = origin_x + j * cell
            y = origin_y + i * cell
            color = _heat_color(val, vmin, vmax, low, high)
            draw.rectangle((x, y, x + cell, y + cell), fill=color, outline=(240, 240, 240))

    return _encode_png(img)


def _render_oklch_scatter(hexes: list[str]) -> str | None:
    if not hexes:
        return None
    width, height = 420, 320
    pad = 32
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    points = []
    max_c = 0.0
    for hx in hexes:
        color = coloraide.Color(hx).convert("oklch")
        l, c_val, _h = color.coords()
        max_c = max(max_c, float(c_val))
        points.append((hx, float(l), float(c_val)))

    max_c = max(max_c, 0.1)
    for hx, l_val, c_val in points:
        x = pad + (c_val / max_c) * (width - 2 * pad)
        y = height - pad - (l_val * (height - 2 * pad))
        radius = 6
        outline = (0, 0, 0) if color_utils.relative_luminance(hx) > 0.6 else (255, 255, 255)
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=hx,
            outline=outline,
        )

    draw.line((pad, pad, pad, height - pad), fill=(0, 0, 0))
    draw.line((pad, height - pad, width - pad, height - pad), fill=(0, 0, 0))
    return _encode_png(img)


def _render_temperature_bar(summary: dict[str, int]) -> str | None:
    if not summary:
        return None
    categories = ["warm", "cool", "neutral"]
    counts = [summary.get(cat, 0) for cat in categories]
    max_count = max(counts) if counts else 0
    if max_count == 0:
        return None
    width, height = 360, 160
    pad = 24
    bar_width = (width - 2 * pad) // len(categories)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    colors = {
        "warm": (220, 90, 70),
        "cool": (70, 130, 200),
        "neutral": (160, 160, 160),
    }
    for idx, cat in enumerate(categories):
        count = counts[idx]
        bar_height = int((count / max_count) * (height - 2 * pad))
        x0 = pad + idx * bar_width
        y0 = height - pad - bar_height
        x1 = x0 + bar_width - 8
        y1 = height - pad
        draw.rectangle((x0, y0, x1, y1), fill=colors[cat], outline=(0, 0, 0))
    return _encode_png(img)


def build_color_science_artifacts(
    colors: Sequence[Any],
    *,
    max_colors: int = 10,
    exclude_state_variants: bool = True,
) -> ColorScienceArtifacts:
    palette_colors = _select_palette_colors(
        colors, max_colors=max_colors, exclude_state_variants=exclude_state_variants
    )
    palette_hexes = _normalize_hexes(palette_colors)
    if not palette_hexes:
        return ColorScienceArtifacts(images=[], json=[])
    palette_weights = _palette_weights(palette_colors, max_colors)[: len(palette_hexes)]

    metrics = _build_metrics(palette_hexes)
    diversity = color_utils.get_perceptual_distance_summary(palette_hexes)
    delta_e = _delta_e_matrix(palette_hexes)
    contrast = _contrast_matrix(palette_hexes)

    temperature_summary = {"warm": 0, "cool": 0, "neutral": 0}
    for item in metrics:
        temp = item.get("temperature")
        if temp in temperature_summary:
            temperature_summary[temp] += 1

    images: list[dict[str, Any]] = []
    json_items: list[dict[str, Any]] = []

    palette_strip = generate_palette_strip(palette_hexes)
    if palette_strip:
        images.append(
            {
                "type": "palette-strip",
                "base64": palette_strip,
                "description": "Palette swatch strip",
            }
        )

    palette_histogram = generate_palette_histogram(palette_hexes, palette_weights)
    if palette_histogram:
        images.append(
            {
                "type": "palette-histogram",
                "base64": palette_histogram,
                "description": "Palette prominence histogram",
            }
        )

    oklch_scatter = _render_oklch_scatter(palette_hexes)
    if oklch_scatter:
        images.append(
            {
                "type": "oklch-scatter",
                "base64": oklch_scatter,
                "description": "OKLCH scatter (L vs C, hue encoded)",
            }
        )

    delta_e_heatmap = _render_heatmap(
        palette_hexes,
        delta_e,
        low=(245, 245, 245),
        high=(200, 60, 60),
    )
    if delta_e_heatmap:
        images.append(
            {
                "type": "delta-e-heatmap",
                "base64": delta_e_heatmap,
                "description": "Delta-E distance heatmap",
            }
        )

    contrast_heatmap = _render_heatmap(
        palette_hexes,
        contrast,
        low=(200, 60, 60),
        high=(70, 160, 90),
    )
    if contrast_heatmap:
        images.append(
            {
                "type": "contrast-heatmap",
                "base64": contrast_heatmap,
                "description": "Contrast ratio heatmap",
            }
        )

    temperature_bar = _render_temperature_bar(temperature_summary)
    if temperature_bar:
        images.append(
            {
                "type": "temperature-bar",
                "base64": temperature_bar,
                "description": "Warm/cool/neutral counts",
            }
        )

    json_items.append(
        {
            "type": "color-metrics",
            "payload": {"colors": metrics},
        }
    )
    json_items.append(
        {
            "type": "palette-diversity",
            "payload": diversity,
        }
    )
    json_items.append(
        {
            "type": "delta-e-matrix",
            "payload": {"hexes": palette_hexes, "matrix": delta_e},
        }
    )
    json_items.append(
        {
            "type": "contrast-matrix",
            "payload": {"hexes": palette_hexes, "matrix": contrast},
        }
    )
    json_items.append(
        {
            "type": "temperature-summary",
            "payload": temperature_summary,
        }
    )

    return ColorScienceArtifacts(images=images, json=json_items)
