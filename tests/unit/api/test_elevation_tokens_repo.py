import pytest

spacing = pytest.importorskip("copy_that.interfaces.api.spacing")
from copy_that.application.spacing_models import SpacingExtractionResult, SpacingScale, SpacingToken


def test_elevation_tokens_flow_into_design_tokens():
    result = SpacingExtractionResult(
        tokens=[
            SpacingToken(
                value_px=8,
                name="spacing-sm",
                semantic_role="layout",
                spacing_type=None,
                category="cv",
                confidence=0.9,
                count=1,
                prominence_percentage=None,
                scale_position=0,
                scale_system=SpacingScale.FOUR_POINT,
                base_unit=8,
                grid_aligned=True,
                grid_deviation_px=None,
                usage=["layout"],
                related_tokens=None,
                extraction_metadata=None,
            )
        ],
        scale_system=SpacingScale.FOUR_POINT,
        base_unit=8,
        base_unit_confidence=0.9,
        grid_compliance=1.0,
        extraction_confidence=0.9,
        min_spacing=8,
        max_spacing=8,
        unique_values=[8],
        elevation_tokens=[
            {
                "id": "token/elevation/1",
                "type": "shadow",
                "value": [{"x": 2, "y": 4, "blur": 8, "spread": 0, "color": "rgba(0,0,0,0.2)"}],
                "attributes": {"role": "elevation", "level": 1},
            }
        ],
    )
    response = spacing._result_to_response(result)  # type: ignore[attr-defined]
    assert response.design_tokens is not None
    assert "shadow" in response.design_tokens
    assert any("token/elevation/1" in response.design_tokens["shadow"] for _ in response.design_tokens["shadow"])
