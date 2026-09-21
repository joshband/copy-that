"""End-to-end pipeline that turns a control-panel image into W3C tokens."""

from __future__ import annotations

import logging
from io import BytesIO
from os import PathLike
from typing import Any

from PIL import Image

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.graph import TokenGraph
from copy_that.core_tokens.model import RelationType, Token, TokenRelation, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.extractors.color.cv_extractor import CVColorExtractor
from copy_that.extractors.cv.control_classifier import ControlCandidate, ControlClassifier
from copy_that.extractors.cv.preprocess import preprocess_image
from copy_that.extractors.cv.primitives import (
    detect_circles,
    detect_lines,
    detect_rectangles,
)
from copy_that.shadowlab.stages_v2 import run_pipeline_v2
from layout.layout_graph import PanelGraph
from typography.recommender import recommend_typography

logger = logging.getLogger(__name__)


def process_panel_image(image_path: str | PathLike[str]) -> dict[str, Any]:
    """Run the full CV + token graph pipeline on an image path."""
    repo = InMemoryTokenRepository()
    graph = TokenGraph(repo)
    data = preprocess_image(str(image_path))
    _extract_colors(data["pil_image"], graph)
    candidates = _build_control_candidates(data)
    instances = ControlClassifier().classify(candidates, data["cv_bgr"])
    layout_graph = PanelGraph.from_instances(instances)
    color_roles = _color_role_map(graph)
    if color_roles:
        recommend_typography(layout_graph, repo, color_tokens=color_roles)
    _add_shadow_tokens(str(image_path), repo, color_roles)
    _log_token_validation(graph, strict=True)
    return tokens_to_w3c_flat(repo)


def _extract_colors(image: Image.Image, graph: TokenGraph) -> None:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    CVColorExtractor().extract_from_bytes(
        buffer.getvalue(), token_repo=graph.repo, token_namespace="token/color/panel"
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


def _color_role_map(graph: TokenGraph) -> dict[str, str]:
    colors = graph.find_by_type("color")
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


def _log_token_validation(graph: TokenGraph, strict: bool = False) -> None:
    """Log token graph integrity without altering the output payload."""

    report = graph.validate(strict=strict)
    if report["cycle_count"] or report["dangling_relations"]:
        logger.warning("Token graph validation issues: %s", report)
    else:
        logger.debug("Token graph validated cleanly.")


def _add_shadow_tokens(
    image_path: str, repo: InMemoryTokenRepository, color_roles: dict[str, str]
) -> None:
    """Run shadow extraction and record shadow tokens into the repository."""

    try:
        shadow_result = run_pipeline_v2(image_path, high_quality=False)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Shadow pipeline failed; continuing without shadow tokens: %s", exc)
        return

    tokens = shadow_result.get("shadow_tokens")
    artifacts = shadow_result.get("artifacts", {})
    if tokens is None:
        logger.warning("Shadow pipeline returned no tokens")
        return

    primary_color = color_roles.get("primary") if color_roles else None
    relations = (
        [
            TokenRelation(
                type=RelationType.COMPOSES, target=primary_color, meta={"role": "shadow-color"}
            )
        ]
        if primary_color
        else []
    )

    attributes = {
        "coverage": getattr(tokens, "coverage", None),
        "mean_strength": getattr(tokens, "mean_strength", None),
        "edge_softness_mean": getattr(tokens, "edge_softness_mean", None),
        "edge_softness_std": getattr(tokens, "edge_softness_std", None),
        "physics_consistency": getattr(tokens, "physics_consistency", None),
        "key_light_softness": getattr(tokens, "key_light_softness", None),
        "shadow_strategy": artifacts.get("strategy_notes") or "",
    }

    layer = {
        key: value
        for key, value in {
            "coverage": attributes["coverage"],
            "strength": attributes["mean_strength"],
            "softness": attributes["edge_softness_mean"],
            "lightSoftness": attributes["key_light_softness"],
            "color": primary_color,
        }.items()
        if value is not None
    }

    repo.upsert_token(
        Token(
            id="token/shadow/panel",
            type=TokenType.SHADOW,
            value=[layer],
            attributes=attributes,
            relations=relations,
        )
    )
