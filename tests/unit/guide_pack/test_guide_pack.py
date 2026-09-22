"""Guide Pack schema + builder tests."""

from __future__ import annotations

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.guide_pack import GuidePack, build_guide_pack, render_guide_html
from copy_that.guide_pack.schema import snapshot_hash


def test_guide_pack_schema_and_builder():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="color.primary",
            type=TokenType.COLOR,
            value="#112233",
            attributes={"hex": "#112233", "source": "cv", "confidence": 0.9, "role": "primary"},
        )
    )
    repo.upsert_token(
        Token(
            id="gradient.linear-cv-01",
            type=TokenType.GRADIENT,
            value={
                "type": "linear",
                "angle": 90,
                "stops": [
                    {"position": 0, "color": "#112233"},
                    {"position": 1, "color": "#445566"},
                ],
            },
            attributes={"source": "cv", "confidence": 0.8},
        )
    )
    repo.upsert_token(
        Token(
            id="duration.fast",
            type="duration",
            value={"value": 150, "unit": "ms"},
            attributes={"$type": "duration", "source": "preset", "confidence": 0.2},
        )
    )

    pack = build_guide_pack(repo, project_id=7, project_name="Demo Brand")
    assert isinstance(pack, GuidePack)
    assert pack.meta.project_id == 7
    assert pack.meta.token_snapshot_hash == snapshot_hash(pack.meta.token_ids)
    assert "color.primary" in pack.foundations.colors
    assert pack.foundations.gradients
    assert pack.meta.source_counts.get("extract", 0) >= 1
    assert pack.meta.source_counts.get("preset", 0) >= 1
    assert "gradient" in pack.meta.type_coverage
    assert pack.brand.palette_roles.get("primary") == "color.primary"

    meta = pack.to_component_meta()
    assert meta["brand"]["name"] == "Demo Brand"
    assert meta["token_snapshot_hash"] == pack.meta.token_snapshot_hash

    html = render_guide_html(pack)
    assert "Demo Brand" in html
    assert "13-type honesty" in html
    assert "illustrative" in html.lower()


def test_namespaced_extensions_on_guide_related_export():
    from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat

    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="color.primary",
            type=TokenType.COLOR,
            value="#AABBCC",
            attributes={"hex": "#AABBCC", "source": "synth", "confidence": 0.4, "role": "primary"},
        )
    )
    flat = tokens_to_w3c_flat(repo)
    entry = flat["color"]["color.primary"]
    ext = entry["$extensions"]
    assert ext["com.copythat.source"] == "synth"
    assert ext["com.copythat.confidence"] == 0.4
    assert ext["com.copythat.role"] == "primary"
    assert "confidence" not in entry
    assert "source" not in entry
    assert "role" not in entry
