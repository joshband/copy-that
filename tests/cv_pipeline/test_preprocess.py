import io

from PIL import Image

from cv_pipeline import preprocess


def _make_png(
    size: tuple[int, int] = (2000, 1000), color: tuple[int, int, int] = (255, 0, 0)
) -> bytes:
    image = Image.new("RGB", size, color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_preprocess_image_returns_expected_shapes(tmp_path) -> None:
    image_path = tmp_path / "panel.png"
    image_path.write_bytes(_make_png())

    result = preprocess.preprocess_image(str(image_path))

    pil_image = result["pil_image"]
    cv_bgr = result["cv_bgr"]
    cv_gray = result["cv_gray"]

    assert pil_image.width <= preprocess.MAX_DIM
    assert cv_bgr.shape[:2] == (pil_image.height, pil_image.width)
    assert cv_gray.shape[:2] == (pil_image.height, pil_image.width)
