from io import BytesIO

import pytest
from PIL import Image

from copy_that.pipeline.preprocessing.enhancer import EnhancementError, ImageEnhancer


def _create_image_bytes(color=(255, 0, 0), size=(64, 64)) -> bytes:
    img = Image.new("RGB", size, color)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_enhance_returns_expected_metadata(tmp_path):
    enhancer = ImageEnhancer(max_width=32, max_height=32, output_format="png")
    image_bytes = _create_image_bytes()

    result = enhancer.enhance(image_bytes)

    assert result["format"] == "png"
    assert result["width"] <= 32 and result["height"] <= 32
    assert isinstance(result["data"], bytes)


def test_enhance_invalid_bytes_raises():
    enhancer = ImageEnhancer()
    with pytest.raises(EnhancementError):
        enhancer.enhance(b"notanimage")
