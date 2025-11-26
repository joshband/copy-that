import io

from PIL import Image

from copy_that.application.cv.color_cv_extractor import CVColorExtractor
from core.tokens.repository import InMemoryTokenRepository


def _make_image_bytes(color: tuple[int, int, int] = (255, 0, 0)) -> bytes:
    img = Image.new("RGB", (4, 4), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_extract_from_bytes_writes_tokens_to_repository() -> None:
    extractor = CVColorExtractor(max_colors=2)
    repo = InMemoryTokenRepository()

    result = extractor.extract_from_bytes(
        _make_image_bytes(),
        token_repo=repo,
        token_namespace="token/color/test",
    )

    assert result.colors
    stored = repo.find_by_type("color")
    assert stored
    assert stored[0].id.startswith("token/color/test")
    assert stored[0].attributes["hex"].startswith("#")
