import numpy as np
from PIL import Image

from copy_that.application.cv.layout_text_detector import (
    TextToken,
    attach_text_to_components,
    detect_image_mode,
    run_layoutparser_text,
)


class DummyBlock:
    def __init__(self, coordinates, block_type="Text", score=0.9, text="hello"):
        self.coordinates = coordinates
        self.type = block_type
        self.score = score
        self._text = text

    def crop_image(self, image):
        return image


class DummyLayout:
    def __init__(self, items):
        self._items = items

    def __iter__(self):
        return iter(self._items)


class DummyTesseractAgent:
    def __init__(self, text):
        self._text = text

    def detect(self, image):
        return self._text


class DummyLP:
    def __init__(self, text="ok"):
        self._text = text

    class _DummyModel:
        def __init__(self, text):
            self._text = text

        def detect(self, img):
            return DummyLayout([DummyBlock((0, 0, 10, 10), "Text", 0.8, self._text)])

    def AutoLayoutModel(self, *args, **kwargs):
        return self._DummyModel(self._text)

    def TesseractAgent(self, *args, **kwargs):
        return DummyTesseractAgent(self._text)


def test_attach_text_to_components_matches_on_iou():
    comps = [{"box": (0, 0, 20, 20)}]
    text_tokens = [TextToken(id="t1", bbox=(5, 5, 10, 10), text="label", score=0.9)]
    updated, residual = attach_text_to_components(comps, text_tokens, iou_threshold=0.1)
    assert updated[0]["text"] == "label"
    assert updated[0]["text_confidence"] == 0.9
    assert residual == []


def test_attach_text_to_components_residual_when_no_overlap():
    comps = [{"box": (100, 100, 10, 10)}]
    text_tokens = [TextToken(id="t1", bbox=(0, 0, 5, 5), text="far", score=0.5)]
    updated, residual = attach_text_to_components(comps, text_tokens, iou_threshold=0.5)
    assert updated[0].get("text") is None
    assert len(residual) == 1
    assert residual[0].text == "far"


def test_detect_image_mode_heuristic_ui_vs_photo():
    # Clean edges → likely ui_screenshot
    img_ui = np.zeros((100, 100), dtype=np.uint8)
    img_ui[20:80, 20:80] = 255
    assert detect_image_mode(img_ui) in {"ui_screenshot", "ai_panel", "photo"}
    # Very low edge density → photo
    img_photo = np.full((100, 100), 128, dtype=np.uint8)
    assert detect_image_mode(img_photo) in {"photo", "ai_panel"}


def test_run_layoutparser_text_enabled(monkeypatch):
    # Force ENABLE_LAYOUTPARSER_TEXT on and supply dummy LP/Tesseract
    monkeypatch.setenv("ENABLE_LAYOUTPARSER_TEXT", "1")
    monkeypatch.setenv("LP_DISABLE_DOWNLOAD", "1")
    dummy = DummyLP(text="hello world")
    monkeypatch.setattr(
        "copy_that.application.cv.layout_text_detector._try_import_layoutparser", lambda: dummy
    )
    img = Image.new("RGB", (32, 32), color="white")
    tokens = run_layoutparser_text(img, image_mode="ui_screenshot", enabled=None)
    assert tokens
    assert tokens[0].text.startswith("hello")


def test_run_layoutparser_text_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_LAYOUTPARSER_TEXT", "0")
    img = Image.new("RGB", (16, 16), color="white")
    tokens = run_layoutparser_text(img, image_mode="ui_screenshot", enabled=None)
    assert tokens == []
