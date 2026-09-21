"""Classical shadow extraction confidence from area/softness/contrast."""

from __future__ import annotations

from copy_that.shadowlab.tokens import ShadowFeatures, compute_classical_extraction_confidence


def _features(**overrides: float) -> ShadowFeatures:
    base: dict = dict(
        shadow_area_fraction=0.0,
        mean_shadow_intensity=0.3,
        mean_lit_intensity=0.8,
        mean_shadow_to_lit_ratio=0.375,
        edge_softness_mean=0.5,
        edge_softness_std=0.1,
        dominant_light_direction=None,
        inconsistency_score=0.1,
        shadow_contrast=0.4,
        shadow_count_major=1,
        light_direction_confidence=0.0,
    )
    base.update(overrides)
    return ShadowFeatures(**base)


def test_classical_conf_flat_image_is_zero():
    assert compute_classical_extraction_confidence(_features(shadow_area_fraction=0.0005)) == 0.0


def test_classical_conf_with_cues_is_mid_high():
    conf = compute_classical_extraction_confidence(
        _features(
            shadow_area_fraction=0.12,
            edge_softness_mean=0.55,
            shadow_contrast=0.35,
            mean_shadow_intensity=0.25,
            mean_lit_intensity=0.85,
            light_direction_confidence=0.0,
        )
    )
    assert 0.35 <= conf <= 0.85


def test_classical_conf_boosts_with_light_direction():
    without = compute_classical_extraction_confidence(
        _features(shadow_area_fraction=0.1, edge_softness_mean=0.5, shadow_contrast=0.3)
    )
    with_light = compute_classical_extraction_confidence(
        _features(
            shadow_area_fraction=0.1,
            edge_softness_mean=0.5,
            shadow_contrast=0.3,
            light_direction_confidence=0.8,
        )
    )
    assert with_light >= without
