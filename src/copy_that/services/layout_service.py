"""Service helpers for layout / shape tokens."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository, TokenRepository
from copy_that.domain.layout_tokens import LayoutTokenCreate


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "token"


def core_token_to_create(token: Token) -> LayoutTokenCreate | None:
    """Convert an in-memory layout Token into a DB create DTO."""
    role = str(token.attributes.get("role") or "layout")
    value = token.value
    value_json: str | None = None
    value_px = 0.0

    if isinstance(value, dict):
        value_json = json.dumps(value)
        if "radius" in value and value["radius"] is not None:
            value_px = float(value["radius"])
        elif "border" in value:
            border = value["border"]
            if isinstance(border, dict) and border.get("width") is not None:
                value_px = float(border["width"])
            elif border is not None:
                value_px = float(border)
        elif value.get("px") is not None:
            value_px = float(value["px"])
        elif value.get("columns") is not None:
            value_px = float(value["columns"])
        else:
            return None
    elif isinstance(value, (int, float)):
        value_px = float(value)
        value_json = json.dumps({"px": value_px})
    else:
        return None

    name = token.id.rsplit("/", 1)[-1] if "/" in token.id else token.id
    confidence = float(token.attributes.get("confidence") or 0.8)
    return LayoutTokenCreate(
        name=name,
        role=role,
        value_px=value_px,
        value_json=value_json,
        confidence=confidence,
    )


def tokens_to_creates(tokens: Sequence[Token]) -> list[LayoutTokenCreate]:
    creates: list[LayoutTokenCreate] = []
    for token in tokens:
        create = core_token_to_create(token)
        if create is not None:
            creates.append(create)
    return creates


def db_layout_to_repo(tokens: Sequence[Any], namespace: str) -> TokenRepository:
    """Build a TokenRepository of LAYOUT tokens from DB rows."""
    repo = InMemoryTokenRepository()
    for index, row in enumerate(tokens, start=1):
        role = getattr(row, "role", None) or "layout"
        name = getattr(row, "name", None) or f"{role}-{index}"
        value_px = float(getattr(row, "value_px", 0) or 0)
        value_json = getattr(row, "value_json", None)
        confidence = float(getattr(row, "confidence", 0.8) or 0.8)

        parsed: dict[str, Any] | None = None
        if isinstance(value_json, str) and value_json:
            try:
                loaded = json.loads(value_json)
                if isinstance(loaded, dict):
                    parsed = loaded
            except json.JSONDecodeError:
                parsed = None

        if parsed is not None:
            value: Any = parsed
        elif role == "corner_radius":
            value = {"radius": value_px}
        elif role == "border_width":
            value = {"border": {"width": value_px}}
        elif role == "grid_columns":
            value = {"columns": int(value_px)}
        else:
            value = {"px": value_px}

        token_id = f"{namespace}/{_slug(role)}/{index}"
        if getattr(row, "name", None):
            token_id = f"{namespace}/{_slug(str(name))}"

        repo.upsert_token(
            Token(
                id=token_id,
                type=TokenType.LAYOUT,
                value=value,
                attributes={"role": role, "confidence": confidence, "name": name},
            )
        )
    return repo


def synthesize_opacity_tokens_from_shadows(
    shadows: Sequence[Any], namespace: str = "opacity"
) -> list[Token]:
    """Derive unique opacity number tokens from persisted shadow opacities."""
    tokens: list[Token] = []
    seen: set[float] = set()
    for shadow in shadows:
        raw = getattr(shadow, "opacity", None)
        if raw is None:
            continue
        try:
            opacity = round(float(raw), 3)
        except (TypeError, ValueError):
            continue
        if opacity in seen:
            continue
        seen.add(opacity)

        role = getattr(shadow, "semantic_role", None) or getattr(shadow, "name", None) or "shadow"
        slug = _slug(str(role))
        # Prefer opacity.shadow-* naming from the P2a brief
        if not slug.startswith("shadow"):
            slug = f"shadow-{slug}"
        token_id = f"{namespace}.{slug}"
        # Deduplicate ids if multiple shadows share a role but we already uniqued by opacity;
        # append rounded opacity when id collides.
        if any(t.id == token_id for t in tokens):
            token_id = f"{namespace}.{slug}-{str(opacity).replace('.', '-')}"

        tokens.append(
            Token(
                id=token_id,
                type="opacity",
                value=opacity,
                attributes={
                    "$type": "number",
                    "role": "opacity",
                    "source": "shadow",
                    "confidence": 0.75,
                    "shadow_name": getattr(shadow, "name", None),
                },
            )
        )
    return tokens
