import io

from PIL import Image

from copy_that.application.cv.color_cv_extractor import CVColorExtractor


def make_image(bg_hex: str, fg_hex: str) -> bytes:
    bg_rgb = tuple(int(bg_hex[i : i + 2], 16) for i in (1, 3, 5))
    fg_rgb = tuple(int(fg_hex[i : i + 2], 16) for i in (1, 3, 5))
    img = Image.new("RGB", (100, 100), bg_rgb)
    for x in range(40, 60):
        for y in range(40, 60):
            img.putpixel((x, y), fg_rgb)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_background_token_detected_and_first():
    data = make_image("#cccccc", "#ff0000")
    extractor = CVColorExtractor(max_colors=5)
    result = extractor.extract_from_bytes(data)

    assert result.background_colors
    assert result.background_colors[0].lower() == "#cccccc"
    assert result.colors
    assert result.colors[0].background_role == "primary"
    assert result.colors[0].hex.lower().startswith("#cc")
    # Background hex should not be duplicated later
    assert sum(1 for c in result.colors if c.hex.lower() == "#cccccc") == 1
