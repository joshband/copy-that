"""End-to-end pipeline that turns a control-panel image into W3C tokens."""

from __future__ import annotations

from io import BytesIO
from os import PathLike
from typing import Any

from PIL import Image

from copy_that.application.cv.color_cv_extractor import CVColorExtractor
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.repository import InMemoryTokenRepository, TokenRepository
from cv_pipeline.control_classifier import ControlCandidate, ControlClassifier
from cv_pipeline.preprocess import preprocess_image
from cv_pipeline.primitives import (
    detect_circles,
    detect_lines,
    detect_rectangles,
)
from layout.layout_graph import PanelGraph
from typography.recommender import recommend_typography


def process_panel_image(image_path: str | PathLike[str]) -> dict[str, Any]:
    """Run the full CV + token graph pipeline on an image path."""
    repo = InMemoryTokenRepository()
    data = preprocess_image(str(image_path))
    _extract_colors(data["pil_image"], repo)
    candidates = _build_control_candidates(data)
    instances = ControlClassifier().classify(candidates, data["cv_bgr"])
    graph = PanelGraph.from_instances(instances)
    color_roles = _color_role_map(repo)
    if color_roles:
        recommend_typography(graph, repo, color_tokens=color_roles)
    return tokens_to_w3c(repo)


def _extract_colors(image: Image.Image, repo: TokenRepository) -> None:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    CVColorExtractor().extract_from_bytes(
        buffer.getvalue(), token_repo=repo, token_namespace="token/color/panel"
    )


def _build_control_candidates(data: dict[str, Any]) -> list[ControlCandidate]:
    gray = data["cv_gray"]
    candidates: list[ControlCandidate] = []
    for circle in detect_circles(gray):
        bbox = (
            int(circle.center[0] - circle.radius),
            int(circle.center[1] - circle.radius),
            int(circle.radius * 2),
            int(circle.radius * 2),
        )
        candidates.append(ControlCandidate(primitive=circle, bbox=bbox))
    for rect in detect_rectangles(gray):
        bbox = (rect.x, rect.y, rect.width, rect.height)
        candidates.append(ControlCandidate(primitive=rect, bbox=bbox))
    for line in detect_lines(gray):
        min_x = min(line.start[0], line.end[0])
        min_y = min(line.start[1], line.end[1])
        max_x = max(line.start[0], line.end[0])
        max_y = max(line.start[1], line.end[1])
        bbox = (min_x, min_y, max_x - min_x or 1, max_y - min_y or 1)
        candidates.append(ControlCandidate(primitive=line, bbox=bbox))
    return candidates


def _color_role_map(repo: TokenRepository) -> dict[str, str]:
    colors = repo.find_by_type("color")
    if not colors:
        return {}
    ranked = sorted(
        colors,
        key=lambda token: token.attributes.get("prominence_percentage", 0),
        reverse=True,
    )
    primary = ranked[0].id
    accent = ranked[1].id if len(ranked) > 1 else primary
    muted = ranked[2].id if len(ranked) > 2 else primary
    return {"primary": primary, "accent": accent, "muted": muted}
