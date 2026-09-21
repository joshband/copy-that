"""Export-time synthesis for full DTCG 2025.10 type coverage (A + Compat+).

Derives or presets missing `$type`s from tokens already on the graph so every
official type can appear in `/export/w3c` without claiming screenshot extraction.

Phase 2: fontFamily/fontWeight and dimension companions are preferably dual-written
at typography/spacing build time; synthesis here remains the export fallback.

Phase 3: prefer CV/heuristic border + strokeStyle and first-class opacity from
shadows/UI alpha when confidence ≥ threshold; presets remain fallback only.

Phase 4: gradients are extracted via CV band/stop clustering (optional palette
confirm); color-pair synth in motion_service is fallback only when confidence
is below threshold or no extract landed.

Phase 5: duration / cubicBezier / transition from UI-kit / style cues when
confidence ≥ threshold; presets remain low-confidence fallback only.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from copy_that.core_tokens.model import RelationType, Token, TokenRelation, TokenType
from copy_that.core_tokens.repository import TokenRepository
from copy_that.core_tokens.spacing import (
    attach_dimension_companion,
    dimension_companion_id,
    make_dimension_companion,
)
from copy_that.core_tokens.typography import (
    font_family_atom_id,
    font_weight_atom_id,
    make_font_family_token,
    make_font_weight_token,
)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "token"


def _repo_ids(repo: TokenRepository) -> set[str]:
    if hasattr(repo, "_tokens"):
        return set(repo._tokens.keys())  # type: ignore[attr-defined]
    ids: set[str] = set()
    for token_type in TokenType:
        for token in repo.find_by_type(token_type):
            ids.add(token.id)
    for extra in (
        "fontFamily",
        "fontWeight",
        "strokeStyle",
        "border",
        "transition",
        "dimension",
        "number",
        "opacity",
        "gradient",
        "duration",
        "cubicBezier",
        "shadow",
    ):
        for token in repo.find_by_type(extra):
            ids.add(token.id)
    return ids


def _upsert_new(repo: TokenRepository, token: Token) -> None:
    if token.id not in _repo_ids(repo):
        repo.upsert_token(token)


def _color_hex(row: Any) -> str | None:
    hex_val = getattr(row, "hex", None)
    if isinstance(hex_val, str) and hex_val.startswith("#"):
        return hex_val.upper()
    return None


def _first_color_hex(colors: Sequence[Any], repo: TokenRepository) -> str | None:
    for row in colors:
        hx = _color_hex(row)
        if hx:
            return hx
    for token in repo.find_by_type(TokenType.COLOR):
        if isinstance(token.value, str) and token.value.startswith("#"):
            return token.value.upper()
        hx = token.attributes.get("hex")
        if isinstance(hx, str) and hx.startswith("#"):
            return hx.upper()
    return None


def _first_color_ref(repo: TokenRepository) -> str | None:
    colors = repo.find_by_type(TokenType.COLOR)
    if not colors:
        return None
    return f"{{{colors[0].id}}}"


def _parse_weight(raw: Any) -> int | None:
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def synthesize_font_atoms_from_typography(
    typography_rows: Sequence[Any],
    *,
    repo: TokenRepository | None = None,
) -> list[Token]:
    """Derive atomic fontFamily / fontWeight tokens from typography uniques.

    Export-time fallback when atoms were not dual-written at extract/persist.
    When ``repo`` is provided, also attaches COMPOSES on typography composites
    that still hold literal family/weight values.
    """
    families: list[str] = []
    weights: list[int] = []
    seen_fam: set[str] = set()
    seen_w: set[int] = set()

    for row in typography_rows:
        fam = getattr(row, "font_family", None)
        if isinstance(fam, str) and fam and fam not in seen_fam:
            seen_fam.add(fam)
            families.append(fam)
        w = _parse_weight(getattr(row, "font_weight", None))
        if w is not None and w not in seen_w:
            seen_w.add(w)
            weights.append(w)

    typography_tokens: list[Token] = []
    if repo is not None:
        typography_tokens = list(repo.find_by_type(TokenType.TYPOGRAPHY))
        for token in typography_tokens:
            val = token.value if isinstance(token.value, dict) else {}
            fam = val.get("fontFamily")
            if (
                isinstance(fam, str)
                and fam
                and not fam.startswith("{")
                and not fam.startswith("fontFamily.")
                and not fam.startswith("font.family.")
                and fam not in seen_fam
            ):
                seen_fam.add(fam)
                families.append(fam)
            weight = val.get("fontWeight")
            if isinstance(weight, str) and (
                weight.startswith("{")
                or weight.startswith("fontWeight.")
                or weight.startswith("font.weight.")
            ):
                continue
            w = _parse_weight(weight)
            if w is not None and w not in seen_w:
                seen_w.add(w)
                weights.append(w)

    tokens: list[Token] = [make_font_family_token(fam, source="derived") for fam in families]
    tokens.extend(make_font_weight_token(w, source="derived") for w in weights)

    if repo is not None and tokens:
        # Wire COMPOSES + atom refs on composites that still use literals
        for typo in typography_tokens:
            raw_val = typo.value
            if not isinstance(raw_val, dict):
                continue
            val = raw_val
            new_val = dict(val)
            new_rels = list(typo.relations)
            changed = False

            fam = val.get("fontFamily")
            if (
                isinstance(fam, str)
                and fam
                and not fam.startswith("{")
                and not fam.startswith("fontFamily.")
                and not fam.startswith("font.family.")
            ):
                atom_id = font_family_atom_id(fam)
                new_val["fontFamily"] = atom_id
                if not any(r.target == atom_id for r in new_rels):
                    new_rels.append(
                        TokenRelation(
                            type=RelationType.COMPOSES,
                            target=atom_id,
                            meta={"role": "font-family"},
                        )
                    )
                changed = True

            weight = val.get("fontWeight")
            already_ref = isinstance(weight, str) and weight.startswith(("{", "fontWeight."))
            w = None if already_ref else _parse_weight(weight)
            if w is not None:
                atom_id = font_weight_atom_id(w)
                new_val["fontWeight"] = atom_id
                if not any(r.target == atom_id for r in new_rels):
                    new_rels.append(
                        TokenRelation(
                            type=RelationType.COMPOSES,
                            target=atom_id,
                            meta={"role": "font-weight"},
                        )
                    )
                changed = True

            if changed:
                repo.upsert_token(
                    Token(
                        id=typo.id,
                        type=typo.type,
                        value=new_val,
                        attributes=dict(typo.attributes),
                        relations=new_rels,
                        meta=dict(typo.meta),
                    )
                )

    return tokens


def synthesize_dimension_from_spacing(repo: TokenRepository, *, limit: int = 8) -> list[Token]:
    """Mirror spacing values as DTCG `$type: dimension` companions (Compat+: keep spacing).

    Prefer companions already dual-written at spacing build; this path is export fallback.
    """
    tokens: list[Token] = []
    existing = _repo_ids(repo)
    updated_spacing: list[Token] = []

    for spacing in repo.find_by_type(TokenType.SPACING)[:limit]:
        expected_id = dimension_companion_id(spacing.id)
        if expected_id in existing or any(t.id == expected_id for t in tokens):
            companion = repo.get_token(expected_id)
            if companion is not None:
                linked = attach_dimension_companion(spacing, companion)
                if linked is not spacing:
                    updated_spacing.append(linked)
            continue

        companion = make_dimension_companion(spacing, source="derived")
        if companion is None:
            continue
        if companion.id in existing or any(t.id == companion.id for t in tokens):
            companion = Token(
                id=f"dimension.{_slug(spacing.id)}",
                type=companion.type,
                value=companion.value,
                attributes=dict(companion.attributes),
                relations=list(companion.relations),
                meta=dict(companion.meta),
            )
        tokens.append(companion)
        updated_spacing.append(attach_dimension_companion(spacing, companion))

    for spacing in updated_spacing:
        repo.upsert_token(spacing)
    return tokens


def synthesize_number_from_typography(
    typography_rows: Sequence[Any],
    *,
    repo: TokenRepository | None = None,
) -> list[Token]:
    """Emit number tokens from unique line-height multipliers."""
    tokens: list[Token] = []
    seen: set[float] = set()

    def add(raw: Any, label: str) -> None:
        try:
            num = round(float(raw), 3)
        except (TypeError, ValueError):
            return
        if num in seen:
            return
        seen.add(num)
        tokens.append(
            Token(
                id=f"number.line-height-{_slug(str(num).replace('.', '-'))}",
                type="number",
                value=num,
                attributes={
                    "$type": "number",
                    "role": "line-height",
                    "source": "derived",
                    "label": label,
                },
            )
        )

    for row in typography_rows:
        add(getattr(row, "line_height", None), "line-height")
    if repo is not None:
        for token in repo.find_by_type(TokenType.TYPOGRAPHY):
            val = token.value if isinstance(token.value, dict) else {}
            add(val.get("lineHeight"), token.id)
    return tokens


def synthesize_stroke_style_presets(*, include_dashed: bool = True) -> list[Token]:
    tokens = [
        Token(
            id="strokeStyle.solid",
            type="strokeStyle",
            value="solid",
            attributes={"$type": "strokeStyle", "role": "stroke", "source": "preset"},
        )
    ]
    if include_dashed:
        tokens.append(
            Token(
                id="strokeStyle.dashed",
                type="strokeStyle",
                value="dashed",
                attributes={"$type": "strokeStyle", "role": "stroke", "source": "preset"},
            )
        )
    return tokens


def _layout_border_widths(repo: TokenRepository) -> list[tuple[str, float]]:
    widths: list[tuple[str, float]] = []
    for token in repo.find_by_type(TokenType.LAYOUT):
        role = str(token.attributes.get("role") or "")
        val = token.value
        width: float | None = None
        if role == "border_width" and isinstance(val, dict):
            border = val.get("border")
            if isinstance(border, dict) and border.get("width") is not None:
                width = float(border["width"])
            elif isinstance(border, (int, float)):
                width = float(border)
        elif isinstance(val, dict) and isinstance(val.get("border"), dict):
            bw = val["border"].get("width")
            if bw is not None:
                width = float(bw)
        if width is not None:
            widths.append((token.id, width))
    return widths


def synthesize_border_composites(repo: TokenRepository) -> list[Token]:
    """Compose DTCG border tokens from layout widths + strokeStyle (+ optional color).

    Skips synthesis when confidently extracted border tokens already exist
    (Phase 3 prefer-extract).
    """
    existing = list(repo.find_by_type(TokenType.BORDER)) + list(repo.find_by_type("border"))
    if any(
        str(t.attributes.get("source") or "") in {"cv", "extracted", "heuristic"}
        and float(t.attributes.get("confidence") or 0.7) >= 0.55
        for t in existing
    ):
        return []

    widths = _layout_border_widths(repo)
    if not widths:
        # Fallback default border so the type is present when we have any tokens
        widths = [("synth.default", 1.0)]

    color_ref = _first_color_ref(repo)
    # Prefer confidently extracted dashed style when present
    style_ref = "{strokeStyle.solid}"
    for style_tok in list(repo.find_by_type(TokenType.STROKE_STYLE)) + list(
        repo.find_by_type("strokeStyle")
    ):
        if (
            str(style_tok.value).lower() == "dashed"
            and str(style_tok.attributes.get("source") or "") in {"cv", "extracted", "heuristic"}
            and float(style_tok.attributes.get("confidence") or 0.0) >= 0.55
        ):
            style_ref = f"{{{style_tok.id}}}"
            break

    tokens: list[Token] = []
    for idx, (source_id, width) in enumerate(widths[:4], start=1):
        value: dict[str, Any] = {
            "width": {"value": width, "unit": "px"},
            "style": style_ref,
        }
        if color_ref:
            value["color"] = color_ref
        source = "synth" if source_id == "synth.default" else "derived"
        tokens.append(
            Token(
                id=f"border.default-{idx:02d}",
                type="border",
                value=value,
                attributes={
                    "$type": "border",
                    "role": "border",
                    "source": source,
                    "from": source_id,
                },
            )
        )
    return tokens


def synthesize_transition_composites(
    repo: TokenRepository | None = None,
    *,
    prefer_extracted: bool = True,
    confidence_threshold: float = 0.55,
) -> list[Token]:
    """Compose transition tokens referencing duration + cubicBezier.

    Skips when heuristic/AI transitions already exist. Prefers extracted duration
    / easing refs when present; otherwise stable preset ids. Synth confidence
    stays low — never inflate presets.
    """
    if prefer_extracted and repo is not None:
        try:
            from copy_that.extractors.motion_extract import repo_has_extracted_motion

            if repo_has_extracted_motion(
                repo,
                confidence_threshold=confidence_threshold,
                types={"transition"},
            ):
                return []
        except Exception:
            pass

    duration_fast = "{duration.fast}"
    duration_normal = "{duration.normal}"
    ease = "{cubicBezier.ease}"
    ease_io = "{cubicBezier.ease-in-out}"
    source = "synth"
    confidence = 0.35

    if repo is not None:
        try:
            from copy_that.extractors.motion_extract import repo_has_extracted_motion

            if repo_has_extracted_motion(
                repo,
                confidence_threshold=confidence_threshold,
                types={"duration", "cubicBezier"},
            ):
                source = "extracted"
                confidence = 0.6
        except Exception:
            pass

    return [
        Token(
            id="transition.fast",
            type="transition",
            value={
                "duration": duration_fast,
                "delay": {"value": 0, "unit": "ms"},
                "timingFunction": ease,
            },
            attributes={
                "$type": "transition",
                "role": "transition",
                "source": source,
                "confidence": confidence,
            },
        ),
        Token(
            id="transition.normal",
            type="transition",
            value={
                "duration": duration_normal,
                "delay": {"value": 0, "unit": "ms"},
                "timingFunction": ease_io,
            },
            attributes={
                "$type": "transition",
                "role": "transition",
                "source": source,
                "confidence": confidence,
            },
        ),
    ]


def synthesize_fallback_shadow(colors: Sequence[Any], repo: TokenRepository) -> list[Token]:
    """Soft drop-shadow preset when the project has no extracted shadows."""
    if repo.find_by_type(TokenType.SHADOW):
        return []
    hx = _first_color_hex(colors, repo) or "#000000"
    return [
        Token(
            id="shadow.soft",
            type=TokenType.SHADOW,
            value=[
                {
                    "x": 0,
                    "y": 4,
                    "blur": 12,
                    "spread": 0,
                    "color": hx,
                    "opacity": 0.2,
                }
            ],
            attributes={
                "$type": "shadow",
                "role": "elevation",
                "source": "preset",
                "confidence": 0.4,
            },
        )
    ]


def apply_type_coverage_synthesis(
    repo: TokenRepository,
    *,
    colors: Sequence[Any] = (),
    typography_rows: Sequence[Any] = (),
    has_any_tokens: bool = False,
) -> None:
    """Upsert derived/preset tokens so all 13 DTCG `$type`s can appear on export."""
    if not has_any_tokens:
        return

    for token in synthesize_font_atoms_from_typography(typography_rows, repo=repo):
        _upsert_new(repo, token)

    for token in synthesize_dimension_from_spacing(repo):
        _upsert_new(repo, token)

    # Prefer opacity numbers from shadows / UI alpha; also emit line-height numbers
    try:
        from copy_that.extractors.opacity_extract import opacity_tokens_from_repo

        for token in opacity_tokens_from_repo(repo):
            _upsert_new(repo, token)
    except Exception:
        pass

    for token in synthesize_number_from_typography(typography_rows, repo=repo):
        _upsert_new(repo, token)

    # Guarantee at least one DTCG number token when the graph has any content
    has_number = bool(repo.find_by_type("number")) or bool(repo.find_by_type("opacity"))
    if not has_number:
        _upsert_new(
            repo,
            Token(
                id="number.unity",
                type="number",
                value=1,
                attributes={
                    "$type": "number",
                    "role": "unitless",
                    "source": "preset",
                },
            ),
        )

    # Stroke presets only fill gaps; extracted CV styles win via _upsert_new id check
    has_extracted_stroke = any(
        str(t.attributes.get("source") or "") in {"cv", "extracted", "heuristic"}
        and float(t.attributes.get("confidence") or 0.0) >= 0.55
        for t in list(repo.find_by_type(TokenType.STROKE_STYLE))
        + list(repo.find_by_type("strokeStyle"))
    )
    for token in synthesize_stroke_style_presets(include_dashed=not has_extracted_stroke):
        _upsert_new(repo, token)

    for token in synthesize_border_composites(repo):
        _upsert_new(repo, token)

    for token in synthesize_transition_composites(repo):
        _upsert_new(repo, token)

    for token in synthesize_fallback_shadow(colors, repo):
        _upsert_new(repo, token)
