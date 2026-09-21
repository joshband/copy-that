from copy_that.layoutlab.elevation_tokens import derive_elevation_tokens, summarize_lighting


def test_derive_elevation_tokens_creates_layers():
    tokens = derive_elevation_tokens([[0.1, 0.5], [0.2, 0.9]], levels=3, base_id="token/elev")
    assert len(tokens) == 3
    first = tokens[0]
    assert first.id == "token/elev/1"
    assert first.attributes["role"] == "elevation"
    assert isinstance(first.value, list) and first.value[0]["blur"] > 0


def test_summarize_lighting_defaults():
    summary = summarize_lighting(None, shadow_strength=None)
    assert "lighting_style" in summary
    assert summary["depth_mean"] == 0.5
