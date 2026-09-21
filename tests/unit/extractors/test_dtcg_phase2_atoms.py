"""Phase 2: persist fontFamily/fontWeight atoms + dimension companions."""

from __future__ import annotations

from types import SimpleNamespace

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c, w3c_to_tokens
from copy_that.core_tokens.model import RelationType, Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.extractors import get_extractor
from copy_that.extractors.dtcg_capability import CoverageStatus, capability_for
from copy_that.services.spacing_service import build_spacing_repo
from copy_that.services.type_coverage_service import (
    apply_type_coverage_synthesis,
    synthesize_font_atoms_from_typography,
)
from copy_that.services.typography_service import build_typography_repo


def test_capability_font_atoms_are_derive():
    assert capability_for("fontFamily").status == CoverageStatus.DERIVE
    assert capability_for("fontWeight").status == CoverageStatus.DERIVE
    assert capability_for("dimension").status == CoverageStatus.DERIVE


def test_build_typography_repo_dual_writes_font_atoms_with_composes():
    rows = [
        SimpleNamespace(
            font_family="Inter",
            font_weight=400,
            font_style="normal",
            font_size=16,
            line_height=1.5,
            letter_spacing=None,
            text_transform=None,
            text_align=None,
            semantic_role="body",
            confidence=0.9,
        ),
        SimpleNamespace(
            font_family="Inter",
            font_weight=700,
            font_style="normal",
            font_size=24,
            line_height=1.2,
            letter_spacing=None,
            text_transform=None,
            text_align=None,
            semantic_role="heading",
            confidence=0.9,
        ),
    ]
    repo = build_typography_repo(rows, namespace="token/typography/test")

    fam = repo.get_token("fontFamily.inter")
    assert fam is not None
    assert fam.type == TokenType.FONT_FAMILY_DTCG
    assert fam.value == "Inter"
    assert fam.attributes.get("source") == "extracted"

    w400 = repo.get_token("fontWeight.400")
    w700 = repo.get_token("fontWeight.700")
    assert w400 is not None and w400.value == 400
    assert w700 is not None and w700.value == 700

    typo_tokens = repo.find_by_type(TokenType.TYPOGRAPHY)
    assert len(typo_tokens) == 2
    for typo in typo_tokens:
        assert typo.value["fontFamily"] == "fontFamily.inter"
        targets = {rel.target for rel in typo.relations if rel.type == RelationType.COMPOSES}
        assert "fontFamily.inter" in targets
        assert any(t.startswith("fontWeight.") for t in targets)


def test_build_spacing_repo_dual_writes_dimension_companions():
    rows = [
        SimpleNamespace(value_px=8, value_rem=0.5, confidence=0.8, name="xs"),
        SimpleNamespace(value_px=16, value_rem=1.0, confidence=0.9, name="md"),
    ]
    repo = build_spacing_repo(rows, namespace="token/spacing/test")

    spacing = repo.find_by_type(TokenType.SPACING)
    assert len(spacing) == 2
    dims = repo.find_by_type(TokenType.DIMENSION)
    assert len(dims) == 2

    for sp in spacing:
        companion_ids = [rel.target for rel in sp.relations if rel.type == RelationType.COMPOSES]
        assert companion_ids
        companion = repo.get_token(companion_ids[0])
        assert companion is not None
        assert companion.type == TokenType.DIMENSION
        assert companion.attributes.get("from") == sp.id
        assert companion.attributes.get("source") == "extracted"

    payload = tokens_to_w3c(repo)
    assert "spacing" in payload
    assert "dimension" in payload
    for entry in payload["spacing"].values():
        assert entry["$type"] == "dimension"
    for entry in payload["dimension"].values():
        assert entry["$type"] == "dimension"


def test_font_atoms_round_trip_w3c_sections():
    rows = [
        SimpleNamespace(
            font_family="Roboto",
            font_weight=500,
            font_style="normal",
            font_size=14,
            line_height=1.4,
            letter_spacing=None,
            text_transform=None,
            text_align=None,
            semantic_role="body",
            confidence=0.85,
        )
    ]
    repo = build_typography_repo(rows, namespace="token/typography/rt")
    exported = tokens_to_w3c(repo)

    assert "fontFamily" in exported
    assert "fontWeight" in exported
    assert exported["fontFamily"]["fontFamily.roboto"]["$type"] == "fontFamily"
    assert exported["fontFamily"]["fontFamily.roboto"]["$value"] == "Roboto"
    assert exported["fontWeight"]["fontWeight.500"]["$value"] == 500

    typo_entry = next(iter(exported["typography"].values()))
    assert typo_entry["$value"]["fontFamily"][0] == "{fontFamily.roboto}"
    assert typo_entry["$value"]["fontWeight"] == "{fontWeight.500}"
    assert "fontFamily.roboto" in typo_entry["$extensions"]["composes"]
    assert "fontWeight.500" in typo_entry["$extensions"]["composes"]

    round_trip = InMemoryTokenRepository()
    w3c_to_tokens(exported, round_trip)
    assert round_trip.get_token("fontFamily.roboto") is not None
    assert round_trip.get_token("fontWeight.500") is not None
    rt_typo = next(iter(round_trip.find_by_type(TokenType.TYPOGRAPHY)))
    targets = {rel.target for rel in rt_typo.relations if rel.type == RelationType.COMPOSES}
    assert "fontFamily.roboto" in targets
    assert "fontWeight.500" in targets


def test_export_synth_fallback_still_creates_atoms_when_literals():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="typography.body",
            type=TokenType.TYPOGRAPHY,
            value={"fontFamily": "Inter", "fontWeight": 400, "fontSize": {"px": 16}},
        )
    )
    atoms = synthesize_font_atoms_from_typography([], repo=repo)
    assert any(a.id == "fontFamily.inter" for a in atoms)
    assert any(a.id == "fontWeight.400" for a in atoms)
    for atom in atoms:
        repo.upsert_token(atom)

    typo = repo.get_token("typography.body")
    assert typo is not None
    assert typo.value["fontFamily"] == "fontFamily.inter"
    assert typo.value["fontWeight"] == "fontWeight.400"


def test_derive_extractors_upsert_from_repo():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="typography.body",
            type=TokenType.TYPOGRAPHY,
            value={"fontFamily": "Georgia", "fontWeight": 400},
        )
    )
    repo.upsert_token(
        Token(id="spacing.gap", type=TokenType.SPACING, value={"px": 12, "rem": 0.75})
    )

    fam_ext = get_extractor("fontFamily")
    weight_ext = get_extractor("fontWeight")
    dim_ext = get_extractor("dimension")
    assert fam_ext.coverage_status == CoverageStatus.DERIVE
    fam_ext.derive_and_upsert(repo)
    weight_ext.derive_and_upsert(repo)
    dim_ext.derive_and_upsert(repo)

    assert repo.get_token("fontFamily.georgia") is not None
    assert repo.get_token("fontWeight.400") is not None
    assert any(t.type == TokenType.DIMENSION for t in repo.find_by_type(TokenType.DIMENSION))


def test_coverage_synthesis_skips_duplicate_dimension_companions():
    rows = [SimpleNamespace(value_px=16, value_rem=1.0, confidence=0.9, name="md")]
    repo = build_spacing_repo(rows, namespace="token/spacing/dup")
    before = {t.id for t in repo.find_by_type(TokenType.DIMENSION)}
    apply_type_coverage_synthesis(repo, has_any_tokens=True)
    after = {t.id for t in repo.find_by_type(TokenType.DIMENSION)}
    assert before == after
