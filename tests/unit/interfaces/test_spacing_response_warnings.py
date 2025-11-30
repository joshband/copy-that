from copy_that.application import spacing_models
from copy_that.application.spacing_models import SpacingExtractionResult, SpacingScale, SpacingToken
from copy_that.interfaces.api import spacing


def _token(value_px: int = 8) -> SpacingToken:
    return SpacingToken(
        value_px=value_px,
        name="spacing-8",
        semantic_role="layout",
        spacing_type=None,
        category="test",
        confidence=0.5,
        usage=["layout"],
        scale_position=0,
        base_unit=4,
        scale_system=SpacingScale.FOUR_POINT,
        grid_aligned=True,
        prominence_percentage=None,
    )


def test_spacing_response_includes_warnings_and_common_spacings():
    base_result = SpacingExtractionResult(
        tokens=[_token()],
        scale_system=SpacingScale.FOUR_POINT,
        base_unit=4,
        base_unit_confidence=0.5,
        grid_compliance=1.0,
        extraction_confidence=0.5,
        min_spacing=4,
        max_spacing=8,
        unique_values=[4, 8],
        cv_gap_diagnostics=None,
        base_alignment=None,
        cv_gaps_sample=None,
        baseline_spacing=None,
        component_spacing_metrics=[{"index": 0, "box": [0, 0, 10, 10], "neighbor_gap": 12}],
        grid_detection=None,
        debug_overlay=None,
        warnings=["Only 10% coverage"],
    )

    response = spacing._result_to_response(base_result)  # type: ignore[arg-type]

    assert response.warnings == ["Only 10% coverage"]
    assert response.common_spacings is not None
    assert response.common_spacings[0].value_px == 12


def test_spacing_merge_accumulates_warnings(monkeypatch):
    # Use Pydantic SpacingToken inside merge to avoid SQLAlchemy constructor churn
    monkeypatch.setattr(spacing, "SpacingToken", spacing_models.SpacingToken)
    cv = SpacingExtractionResult(
        tokens=[_token(4)],
        scale_system=SpacingScale.FOUR_POINT,
        base_unit=4,
        base_unit_confidence=0.5,
        grid_compliance=1.0,
        extraction_confidence=0.5,
        min_spacing=4,
        max_spacing=4,
        unique_values=[4],
        cv_gap_diagnostics=None,
        base_alignment=None,
        cv_gaps_sample=None,
        baseline_spacing=None,
        component_spacing_metrics=None,
        grid_detection=None,
        warnings=["cv warning"],
    )
    ai = SpacingExtractionResult(
        tokens=[_token(8)],
        scale_system=SpacingScale.FOUR_POINT,
        base_unit=4,
        base_unit_confidence=0.5,
        grid_compliance=1.0,
        extraction_confidence=0.5,
        min_spacing=8,
        max_spacing=8,
        unique_values=[8],
        cv_gap_diagnostics=None,
        base_alignment=None,
        cv_gaps_sample=None,
        baseline_spacing=None,
        component_spacing_metrics=None,
        grid_detection=None,
        warnings=["ai warning"],
    )

    merged = spacing._merge_spacing(cv, ai)  # type: ignore[arg-type]
    assert merged.warnings
    assert "cv warning" in merged.warnings
    assert "ai warning" in merged.warnings
