"""Scored accuracy floor for the CV extractors on synthetic screenshots with known answers.

Each scene is rendered in-process, so there are no fixture files and no network.
Thresholds are the measured baseline on 2026-10-08 — raise them as extraction
improves; a drop means a regression in the core product, not a flaky test.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import pytest
from coloraide import Color
from PIL import Image, ImageDraw

from copy_that.extractors.color.cv_extractor import CVColorExtractor
from copy_that.extractors.spacing.cv_extractor import CVSpacingExtractor

# ΔE2000 below ~2 is not noticeable; ~5 is "same color, slightly off".
MATCH_DE = 2.0
NEAR_DE = 5.0


@dataclass(frozen=True)
class ColorScene:
    name: str
    background: str
    blocks: tuple[tuple[str, tuple[int, int, int, int]], ...]
    min_precision: float

    @property
    def palette(self) -> list[str]:
        return [self.background, *(fill for fill, _ in self.blocks)]

    def render(self) -> bytes:
        img = Image.new("RGB", (800, 500), self.background)
        draw = ImageDraw.Draw(img)
        for fill, box in self.blocks:
            draw.rectangle(box, fill=fill)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return buf.getvalue()


COLOR_SCENES = (
    ColorScene(
        name="light-dashboard",
        background="#F8FAFC",
        blocks=(
            ("#1E3A8A", (0, 0, 800, 80)),
            ("#F59E0B", (40, 140, 360, 300)),
            ("#10B981", (420, 140, 760, 300)),
            ("#EF4444", (40, 360, 300, 440)),
        ),
        # Baseline: 5 true colors + 2 spurious tints of the amber block.
        min_precision=0.7,
    ),
    ColorScene(
        name="dark-app",
        background="#0F172A",
        blocks=(
            ("#1E293B", (0, 0, 240, 500)),
            ("#38BDF8", (300, 60, 760, 140)),
            ("#E2E8F0", (300, 200, 760, 260)),
            ("#A855F7", (300, 320, 520, 440)),
        ),
        min_precision=0.7,
    ),
)


def _min_de(color: str, candidates: list[str]) -> float:
    ref = Color(color)
    return min(ref.delta_e(Color(c), method="2000") for c in candidates)


@pytest.mark.parametrize("scene", COLOR_SCENES, ids=lambda s: s.name)
def test_color_extraction_recall_and_precision(scene: ColorScene) -> None:
    result = CVColorExtractor().extract_from_bytes(scene.render())
    extracted = [c.hex for c in result.colors]
    assert extracted, "extractor returned no colors"

    recall = sum(_min_de(c, extracted) <= MATCH_DE for c in scene.palette) / len(scene.palette)
    precision = sum(_min_de(c, scene.palette) <= NEAR_DE for c in extracted) / len(extracted)

    print(f"[{scene.name}] recall={recall:.2f} precision={precision:.2f} extracted={extracted}")
    assert recall == 1.0, f"missed a true color (recall {recall:.2f}): {extracted}"
    assert precision >= scene.min_precision, (
        f"too many colors not in the image (precision {precision:.2f}): {extracted}"
    )


def test_spacing_extraction_finds_8px_system() -> None:
    img = Image.new("RGB", (600, 400), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    x = 24
    for _ in range(5):  # row of buttons, 16px apart
        draw.rectangle([x, 40, x + 80, 88], fill="#334155")
        x += 80 + 16
    y = 120
    for _ in range(4):  # stacked cards, 24px apart
        draw.rectangle([24, y, 300, y + 40], fill="#334155")
        y += 40 + 24
    buf = io.BytesIO()
    img.save(buf, "PNG")

    result = CVSpacingExtractor().extract_from_bytes(buf.getvalue())
    values = {int(t.value_px) for t in result.tokens}

    print(f"[spacing] base_unit={result.base_unit} values={sorted(values)}")
    assert result.base_unit == 8
    assert {16, 24} <= values
