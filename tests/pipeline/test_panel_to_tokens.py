from pathlib import Path

from pipeline.panel_to_tokens import process_panel_image


def test_process_panel_image_returns_color_and_typography_tokens() -> None:
    fixture = Path("tests/fixtures/test_image.png")
    tokens = process_panel_image(fixture)

    assert "color" in tokens and tokens["color"]
    assert "typography" in tokens and tokens["typography"]

    headline = tokens["typography"]["token/typography/headline"]["value"]
    color_ref = headline["color"]

    assert color_ref in tokens["color"]
