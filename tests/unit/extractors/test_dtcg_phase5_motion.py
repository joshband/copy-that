"""Phase 5: duration / cubicBezier / transition from UI-kit / style cues."""

from __future__ import annotations

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.extractors import get_extractor
from copy_that.extractors.dtcg_capability import CoverageStatus, capability_for
from copy_that.extractors.motion_extract import (
    CubicBezierExtractor,
    DurationExtractor,
    TransitionExtractor,
    motion_tokens_from_repo,
    repo_has_extracted_motion,
    upsert_motion_from_repo,
)
from copy_that.extractors.motion_heuristic import (
    MOTION_EXTRACT_CONFIDENCE_THRESHOLD,
    detect_ui_kit_profile,
    profile_from_style_cues,
)
from copy_that.generators.plugins.css import CSSGenerator
from copy_that.generators.plugins.format_utils import transition_css_value
from copy_that.services.motion_service import synthesize_transition_tokens
from copy_that.services.type_coverage_service import synthesize_transition_composites


def test_capability_phase5_motion_derive():
    for name in ("duration", "cubicBezier", "transition"):
        cap = capability_for(name)
        assert cap is not None
        assert cap.status == CoverageStatus.DERIVE
        assert "ai" in cap.modalities or "code" in cap.modalities


def test_registry_motion_extractors_are_derive():
    for name, cls in (
        ("duration", DurationExtractor),
        ("cubicBezier", CubicBezierExtractor),
        ("transition", TransitionExtractor),
    ):
        ext = get_extractor(name)
        assert isinstance(ext, cls)
        assert ext.coverage_status == CoverageStatus.DERIVE
        assert ext.token_type == name


def test_motion_image_extract_is_empty():
    # Screenshot path intentionally yields nothing (weak motion signal)
    import asyncio

    assert asyncio.run(DurationExtractor().extract(b"not-an-image")) == []


def test_material_font_and_spacing_detects_kit():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="fontFamily.roboto",
            type=TokenType.FONT_FAMILY_DTCG,
            value="Roboto",
            attributes={"$type": "fontFamily"},
        )
    )
    for px in (8, 16, 24, 32):
        repo.upsert_token(
            Token(
                id=f"spacing.{px}",
                type=TokenType.SPACING,
                value={"value": px, "unit": "px"},
                attributes={},
            )
        )
    repo.upsert_token(
        Token(
            id="layout.radius.8",
            type=TokenType.LAYOUT,
            value={"radius": 8},
            attributes={"role": "corner_radius"},
        )
    )
    kit, conf = detect_ui_kit_profile(repo)
    assert kit == "material"
    assert conf >= MOTION_EXTRACT_CONFIDENCE_THRESHOLD


def test_style_cue_playful_maps_soft():
    name, conf = profile_from_style_cues("playful")
    assert name == "soft"
    assert conf >= MOTION_EXTRACT_CONFIDENCE_THRESHOLD


def test_motion_tokens_from_material_cues_stable_ids():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="fontFamily.roboto",
            type=TokenType.FONT_FAMILY_DTCG,
            value="Roboto",
            attributes={},
        )
    )
    for px in (8, 16, 24):
        repo.upsert_token(
            Token(
                id=f"spacing.{px}",
                type=TokenType.SPACING,
                value={"value": px, "unit": "px"},
            )
        )
    repo.upsert_token(
        Token(
            id="layout.radius.8",
            type=TokenType.LAYOUT,
            value={"radius": 8},
            attributes={"role": "corner_radius"},
        )
    )
    tokens = motion_tokens_from_repo(repo)
    assert tokens
    ids = {t.id for t in tokens}
    assert "duration.fast" in ids
    assert "cubicBezier.ease" in ids
    assert "transition.normal" in ids
    for t in tokens:
        assert t.attributes.get("source") == "heuristic"
        assert float(t.attributes.get("confidence") or 0) >= MOTION_EXTRACT_CONFIDENCE_THRESHOLD
    # Material profile uses 100ms fast (not the 150ms preset)
    fast = next(t for t in tokens if t.id == "duration.fast")
    assert fast.value["value"] == 100


def test_style_hint_ai_source():
    repo = InMemoryTokenRepository()
    # No kit cues — style hint alone
    tokens = motion_tokens_from_repo(repo, style_hint="minimalist")
    assert tokens
    assert all(t.attributes.get("source") == "ai" for t in tokens)
    assert all(
        float(t.attributes.get("confidence") or 0) >= MOTION_EXTRACT_CONFIDENCE_THRESHOLD
        for t in tokens
    )


def test_weak_cues_yield_no_extract():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(id="color.primary", type=TokenType.COLOR, value="#112233", attributes={})
    )
    assert motion_tokens_from_repo(repo) == []


def test_presets_skip_when_extracted_present():
    repo = InMemoryTokenRepository()
    upsert_motion_from_repo(repo, style_hint="playful")
    assert repo_has_extracted_motion(repo)
    presets = synthesize_transition_tokens(repo=repo)
    assert presets == []
    composites = synthesize_transition_composites(repo=repo)
    assert composites == []


def test_presets_have_low_confidence_not_high():
    tokens = synthesize_transition_tokens()
    assert tokens
    for t in tokens:
        assert t.attributes.get("source") == "preset"
        assert float(t.attributes.get("confidence") or 0) < MOTION_EXTRACT_CONFIDENCE_THRESHOLD


def test_extract_overwrites_preset_same_ids():
    repo = InMemoryTokenRepository()
    for token in synthesize_transition_tokens():
        repo.upsert_token(token)
    # Style cue extract should replace preset values on same ids
    upserted = upsert_motion_from_repo(repo, style_hint="material")
    assert upserted
    fast = repo.get_token("duration.fast")
    assert fast is not None
    assert fast.attributes.get("source") == "ai"
    assert fast.value["value"] == 100  # material profile


def test_w3c_and_css_emit_extracted_motion():
    repo = InMemoryTokenRepository()
    upsert_motion_from_repo(repo, style_hint="minimalist")
    payload = tokens_to_w3c(repo)
    assert "duration" in payload
    assert "cubicBezier" in payload
    assert "transition" in payload
    flat = {
        "duration": payload["duration"],
        "cubicBezier": payload["cubicBezier"],
        "transition": payload["transition"],
    }
    css = CSSGenerator(tokens=flat).generate()
    assert "ms" in css
    assert "cubic-bezier(" in css
    # Transition composite shape stays generator-stable
    tval = next(iter(payload["transition"].values()))
    css_t = transition_css_value(tval)
    assert css_t is not None
