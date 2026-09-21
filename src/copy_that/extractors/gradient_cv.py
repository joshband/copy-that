"""CV linear-band / stop clustering for DTCG gradient tokens (Phase 4).

Classical OpenCV heuristics — not a learned model. Detects dominant linear
color ramps via band sampling, then clusters stops. Prefer extract over
color-pair synth when confidence ≥ :data:`GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD`.
"""

from __future__ import annotations

from base64 import b64decode
from typing import Any

# Prefer extract over P2c color-pair synth when confidence meets this bar.
GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD = 0.55

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - optional at import time
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]


def _decode_bgr(input_data: str | bytes) -> Any | None:
    if np is None or cv2 is None:
        return None
    raw = input_data
    if isinstance(raw, str):
        if raw.startswith("data:"):
            raw = raw.split(",", 1)[-1]
        try:
            raw = b64decode(raw)
        except Exception:
            return None
    if not isinstance(raw, (bytes, bytearray)):
        return None
    arr = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return image


def _bgr_to_hex(bgr: Any) -> str:
    b, g, r = (int(round(float(c))) for c in bgr[:3])
    return f"#{r:02X}{g:02X}{b:02X}"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hx = hex_color.lstrip("#")
    if len(hx) == 3:
        hx = "".join(c * 2 for c in hx)
    return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)


def _color_distance(a: str, b: str) -> float:
    """Approx perceptual distance in 0–1 (RGB L2 / √(3·255²))."""
    ra, ga, ba = _hex_to_rgb(a)
    rb, gb, bb = _hex_to_rgb(b)
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5 / 441.67


def _sample_band_profile(image: Any, *, axis: str, samples: int = 32) -> Any:
    """Mean BGR profile along a linear band (horizontal or vertical)."""
    assert np is not None and cv2 is not None
    h, w = image.shape[:2]
    # Downscale for stable banding
    target = 96
    scale = min(1.0, target / float(max(h, w)))
    if scale < 1.0:
        image = cv2.resize(
            image,
            (max(8, int(w * scale)), max(8, int(h * scale))),
            interpolation=cv2.INTER_AREA,
        )
        h, w = image.shape[:2]

    if axis == "horizontal":
        # Color changes left→right → CSS angle 0
        y0, y1 = h // 3, (2 * h) // 3
        strip = image[max(0, y0) : max(y0 + 1, y1), :, :]
        profile = strip.mean(axis=0)  # (w, 3)
        length = profile.shape[0]
    else:
        # Color changes top→bottom → CSS angle 90
        x0, x1 = w // 3, (2 * w) // 3
        strip = image[:, max(0, x0) : max(x0 + 1, x1), :]
        profile = strip.mean(axis=1)  # (h, 3)
        length = profile.shape[0]

    if length < 8:
        return None
    idxs = np.linspace(0, length - 1, num=min(samples, length)).astype(np.int32)
    return profile[idxs]


def _cluster_stops(profile: Any, *, max_stops: int = 5) -> list[dict[str, Any]]:
    """Merge consecutive similar samples into gradient stops."""
    assert np is not None
    if profile is None or len(profile) < 2:
        return []

    # Quantize colors slightly for stability
    rounded = np.round(profile / 8.0) * 8.0
    n = len(rounded)
    segments: list[tuple[int, int, Any]] = []
    start = 0
    for i in range(1, n):
        delta = float(np.linalg.norm(rounded[i] - rounded[start]))
        if delta > 18.0:
            segments.append((start, i - 1, rounded[start]))
            start = i
    segments.append((start, n - 1, rounded[start]))

    # Collapse tiny segments into neighbors
    merged: list[tuple[int, int, Any]] = []
    for seg in segments:
        if merged and (seg[1] - seg[0]) < max(1, n // 16):
            prev = merged[-1]
            merged[-1] = (prev[0], seg[1], prev[2])
        else:
            merged.append(seg)

    if len(merged) < 2:
        # Force endpoints if there is a real color delta across the band
        end_delta = float(np.linalg.norm(rounded[-1] - rounded[0]))
        if end_delta < 25.0:
            return []
        merged = [(0, 0, rounded[0]), (n - 1, n - 1, rounded[-1])]

    # Cap stop count: keep endpoints + largest mid jumps
    if len(merged) > max_stops:
        mids = merged[1:-1]
        mids_sorted = sorted(
            mids,
            key=lambda s: float(np.linalg.norm(s[2] - rounded[0])),
            reverse=True,
        )
        keep = {id(merged[0]), id(merged[-1])}
        for s in mids_sorted[: max_stops - 2]:
            keep.add(id(s))
        merged = [s for s in merged if id(s) in keep]

    stops: list[dict[str, Any]] = []
    for seg_start, seg_end, color in merged:
        mid = (seg_start + seg_end) / 2.0
        position = round(mid / float(max(1, n - 1)), 3)
        stops.append({"position": position, "color": _bgr_to_hex(color)})

    # Normalize endpoints to 0 and 1
    if stops:
        stops[0]["position"] = 0.0
        stops[-1]["position"] = 1.0
    # Deduplicate consecutive identical colors
    deduped: list[dict[str, Any]] = []
    for stop in stops:
        if deduped and deduped[-1]["color"] == stop["color"]:
            deduped[-1]["position"] = stop["position"]
            continue
        deduped.append(stop)
    if len(deduped) < 2:
        return []
    return deduped


def _score_profile(profile: Any, stops: list[dict[str, Any]]) -> float:
    """Confidence from smoothness + stop separation."""
    assert np is not None
    if profile is None or len(stops) < 2:
        return 0.0

    diffs = np.linalg.norm(np.diff(profile.astype(np.float64), axis=0), axis=1)
    total = float(diffs.sum()) + 1e-6
    # Smooth ramps: many small steps; hard UI edges: few huge spikes
    mean_step = float(diffs.mean())
    max_step = float(diffs.max())
    spike_ratio = max_step / (mean_step + 1e-6)
    smoothness = 1.0 / (1.0 + max(0.0, spike_ratio - 3.0) * 0.35)

    # Color travel across band
    travel = float(np.linalg.norm(profile[-1].astype(np.float64) - profile[0]))
    travel_score = min(1.0, travel / 80.0)

    # Prefer 2–4 stops
    stop_bonus = 1.0 if 2 <= len(stops) <= 4 else 0.75

    # Penalize near-identical endpoints
    endpoint_dist = _color_distance(stops[0]["color"], stops[-1]["color"])
    if endpoint_dist < 0.08:
        return 0.0

    conf = 0.35 + 0.35 * smoothness + 0.25 * travel_score
    conf *= stop_bonus
    # Soft boost when total travel is strong
    if travel > 120:
        conf = min(0.95, conf + 0.08)
    return float(min(0.95, max(0.0, conf)))


def extract_gradient_signals_from_image(
    input_data: str | bytes,
    *,
    confidence_threshold: float = GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD,
    max_gradients: int = 2,
) -> list[dict[str, Any]]:
    """Return gradient descriptor dicts from screenshot bytes.

    Each descriptor has ``angle``, ``stops``, ``confidence``, ``source``.
    """
    image = _decode_bgr(input_data)
    if image is None or np is None:
        return []

    candidates: list[dict[str, Any]] = []
    for axis, angle in (("horizontal", 0), ("vertical", 90)):
        profile = _sample_band_profile(image, axis=axis)
        stops = _cluster_stops(profile)
        conf = _score_profile(profile, stops)
        if conf < confidence_threshold or len(stops) < 2:
            continue
        candidates.append(
            {
                "kind": "gradient",
                "type": "linear",
                "angle": angle,
                "stops": stops,
                "confidence": round(conf, 3),
                "source": "cv",
                "axis": axis,
            }
        )

    candidates.sort(key=lambda c: float(c["confidence"]), reverse=True)
    return candidates[:max_gradients]


def confirm_gradient_against_palette(
    signal: dict[str, Any],
    palette_hexes: list[str],
    *,
    match_threshold: float = 0.22,
) -> dict[str, Any]:
    """Optional palette confirm (AI color pipeline stand-in).

    When stop colors sit near extracted palette hexes, bump confidence and set
    ``source`` to ``ai`` (confirmed). Otherwise leave ``source=cv``.
    """
    if not palette_hexes:
        return signal
    stops = signal.get("stops") or []
    if len(stops) < 2:
        return signal

    matches = 0
    for stop in stops:
        color = str(stop.get("color") or "")
        if not color:
            continue
        if any(_color_distance(color, hx) <= match_threshold for hx in palette_hexes):
            matches += 1

    out = dict(signal)
    if matches >= 2 or (matches >= 1 and len(stops) == 2 and matches == len(stops)):
        out["source"] = "ai"
        out["confirmed_by"] = "palette"
        out["confidence"] = round(min(0.95, float(signal.get("confidence") or 0.55) + 0.08), 3)
    return out
