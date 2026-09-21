"""Unit tests for mood_board_local_image_server (mock backend — no mflux/GPU)."""

from __future__ import annotations

import importlib.util
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "mood_board_local_image_server.py"


def _load_shim_module():
    spec = importlib.util.spec_from_file_location("mood_board_local_image_server", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def shim():
    return _load_shim_module()


def test_parse_size_defaults_and_clamps(shim) -> None:
    assert shim.parse_size(None) == (1024, 1024)
    assert shim.parse_size("512x768") == (512, 768)
    assert shim.parse_size("bogus") == (1024, 1024)
    w, h = shim.parse_size("2000x2000")
    assert w == 1024 and h == 1024
    w, h = shim.parse_size("100x100")
    assert w == 256 and h == 256


def test_mock_generate_returns_b64(shim, monkeypatch) -> None:
    monkeypatch.setenv("MOOD_BOARD_LOCAL_IMAGE_BACKEND", "mock")
    # Re-read won't change BACKEND already imported — call generate with mock path
    images = shim._mock_png_b64(64, 64, "test prompt")
    assert isinstance(images, str) and len(images) > 20


def test_images_generations_endpoint_mock(shim, monkeypatch) -> None:
    monkeypatch.setenv("MOOD_BOARD_LOCAL_IMAGE_BACKEND", "mock")

    def fake_generate(prompt: str, width: int, height: int, n: int) -> list[str]:
        return [shim._mock_png_b64(width, height, prompt) for _ in range(n)]

    shim.Handler.generate_fn = staticmethod(fake_generate)

    server = shim.ThreadingHTTPServer(("127.0.0.1", 0), shim.Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.dumps(
            {
                "model": "schnell",
                "prompt": "brushed aluminum knob",
                "n": 1,
                "size": "512x512",
            }
        ).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/images/generations",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        assert "data" in data and data["data"][0]["b64_json"]

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as resp:
            health = json.loads(resp.read().decode())
        assert health["status"] == "ok"
        assert health["openai_images_path"] == "/v1/images/generations"
    finally:
        server.shutdown()
        shim.Handler.generate_fn = staticmethod(shim.generate_images)


def test_missing_prompt_400(shim) -> None:
    def boom(*_a, **_k):
        raise AssertionError("should not generate")

    shim.Handler.generate_fn = staticmethod(boom)
    server = shim.ThreadingHTTPServer(("127.0.0.1", 0), shim.Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/images/generations",
            data=b'{"model":"schnell","prompt":""}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(req, timeout=5)
        assert exc.value.code == 400
    finally:
        server.shutdown()
        shim.Handler.generate_fn = staticmethod(shim.generate_images)
