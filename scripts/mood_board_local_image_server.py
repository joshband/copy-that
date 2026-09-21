#!/usr/bin/env python3
"""
OpenAI Images API shim backed by mflux (FLUX.1-schnell) on Apple Silicon.

Copy That mood board expects:
  POST /v1/images/generations
  { "model", "prompt", "n", "size", "response_format"? }
  → { "created": 0, "data": [ { "b64_json": "..." } ] }

Locked stack (see docs/features/MOOD_BOARD_SPECIFICATION.md):
  Default: MOOD_BOARD_LOCAL_IMAGE_MODEL=dhairyashil/FLUX.1-schnell-mflux-4bit
           + MOOD_BOARD_LOCAL_IMAGE_BASE_MODEL=schnell
  Fallback: set MODEL=schnell → Flux1.from_name(..., quantize=4)
  Z-Image-Turbo is opt-in only (not default).

Usage:
  huggingface-cli login   # or HF_TOKEN=hf_…
  uv run --with mflux --with pillow python scripts/mood_board_local_image_server.py

  # CI / no GPU:
  MOOD_BOARD_LOCAL_IMAGE_BACKEND=mock python scripts/mood_board_local_image_server.py

Env:
  SHIM_HOST / SHIM_PORT                 default 127.0.0.1:8765
  MOOD_BOARD_LOCAL_IMAGE_BACKEND        mflux | mock   (default mflux)
  MOOD_BOARD_LOCAL_IMAGE_MODEL          default dhairyashil/FLUX.1-schnell-mflux-4bit
  MOOD_BOARD_LOCAL_IMAGE_BASE_MODEL     default schnell (required when MODEL is a Hub id)
  MOOD_BOARD_LOCAL_IMAGE_QUANTIZE       4 (default)
  MOOD_BOARD_LOCAL_IMAGE_STEPS          4 (default)
  HF_TOKEN                              optional Hub token

Then in Copy That .env:
  MOOD_BOARD_IMAGE_BASE_URL=http://127.0.0.1:8765/v1
  MOOD_BOARD_IMAGE_API_KEY=local
  MOOD_BOARD_IMAGE_MODEL=schnell
"""

from __future__ import annotations

import base64
import io
import json
import os
import queue
import re
import threading
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

SHIM_HOST = os.getenv("SHIM_HOST", "127.0.0.1")
SHIM_PORT = int(os.getenv("SHIM_PORT", "8765"))
BACKEND = (os.getenv("MOOD_BOARD_LOCAL_IMAGE_BACKEND") or "mflux").strip().lower()
_DEFAULT_HUB_MIRROR = "dhairyashil/FLUX.1-schnell-mflux-4bit"
MODEL_NAME = (os.getenv("MOOD_BOARD_LOCAL_IMAGE_MODEL") or _DEFAULT_HUB_MIRROR).strip()
BASE_MODEL = (os.getenv("MOOD_BOARD_LOCAL_IMAGE_BASE_MODEL") or "schnell").strip()
QUANTIZE = int(os.getenv("MOOD_BOARD_LOCAL_IMAGE_QUANTIZE", "4"))
STEPS = int(os.getenv("MOOD_BOARD_LOCAL_IMAGE_STEPS", "4"))

_flux_lock = threading.Lock()
_flux_model: Any | None = None

# MLX Metal streams are thread-affine: load + generate must share one dedicated thread.
_mlx_jobs: queue.Queue[Any] = queue.Queue()
_mlx_worker_ready = threading.Event()
_mlx_worker_error: list[BaseException] = []
_mlx_worker_started = False
_mlx_start_lock = threading.Lock()


def parse_size(size: str | None) -> tuple[int, int]:
    """Parse OpenAI-style WxH; clamp to multiples of 16 in 256–1024."""
    if not size:
        return 1024, 1024
    match = re.fullmatch(r"(\d+)x(\d+)", str(size).strip())
    if not match:
        return 1024, 1024
    w, h = int(match.group(1)), int(match.group(2))
    w = max(256, min(1024, (w // 16) * 16))
    h = max(256, min(1024, (h // 16) * 16))
    return w or 1024, h or 1024


def _mock_png_b64(width: int, height: int, prompt: str) -> str:
    """Tiny deterministic PNG so CI never needs mflux/GPU."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        # 1x1 PNG
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    img = Image.new("RGB", (max(width, 64), max(height, 64)), (64, 90, 106))
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, img.width - 8, img.height - 8], outline=(240, 237, 232))
    draw.text((16, 16), (prompt or "mock")[:40], fill=(240, 237, 232))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _get_flux() -> Any:
    global _flux_model
    if _flux_model is not None:
        return _flux_model
    with _flux_lock:
        if _flux_model is not None:
            return _flux_model
        name = (MODEL_NAME or _DEFAULT_HUB_MIRROR).strip()
        lower = name.lower()
        # Z-Image-Turbo is ~33GB — too large for 32GB machines; keep opt-in only.
        if lower in ("z-image-turbo", "zimage-turbo", "z-image"):
            from mflux.models.z_image import ZImageTurbo  # type: ignore

            _flux_model = ("zimage", ZImageTurbo(quantize=QUANTIZE))
        elif "/" in name:
            # Pre-quantized Hub mirror, e.g. dhairyashil/FLUX.1-schnell-mflux-4bit
            from mflux.models.common.config.model_config import ModelConfig  # type: ignore
            from mflux.models.flux.variants.txt2img.flux import Flux1  # type: ignore

            base = (BASE_MODEL or "schnell").strip()
            _flux_model = (
                "flux",
                Flux1(
                    model_config=ModelConfig.from_name(model_name=base, base_model=None),
                    model_path=name,
                    quantize=QUANTIZE,
                ),
            )
        else:
            from mflux.models.flux.variants.txt2img.flux import Flux1  # type: ignore

            _flux_model = ("flux", Flux1.from_name(model_name=lower, quantize=QUANTIZE))
        return _flux_model


def _mflux_generate_one(prompt: str, width: int, height: int, seed: int) -> str:
    from PIL import Image as PILImage

    kind, model = _get_flux()
    steps = STEPS if kind == "flux" else max(STEPS, 8)
    result = model.generate_image(
        seed=seed,
        prompt=prompt,
        num_inference_steps=steps,
        height=height,
        width=width,
    )
    pil = result if isinstance(result, PILImage.Image) else getattr(result, "image", None)
    if not isinstance(pil, PILImage.Image):
        raise RuntimeError(f"unsupported image result type: {type(result)!r}")
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _mlx_worker_main() -> None:
    """Own all MLX GPU work so Stream(gpu) stays on one thread."""
    try:
        _get_flux()
        _mlx_worker_ready.set()
    except BaseException as exc:  # noqa: BLE001
        _mlx_worker_error.append(exc)
        _mlx_worker_ready.set()
        return

    while True:
        item = _mlx_jobs.get()
        if item is None:
            break
        result_q, prompt, width, height, n = item
        try:
            images: list[str] = []
            for i in range(n):
                seed = int(time.time() * 1000) % 2_147_483_647 + i
                images.append(_mflux_generate_one(prompt, width, height, seed))
            result_q.put(("ok", images))
        except BaseException as exc:  # noqa: BLE001
            result_q.put(("err", exc))


def _ensure_mlx_worker(*, timeout_s: float = 600.0) -> None:
    global _mlx_worker_started
    with _mlx_start_lock:
        if not _mlx_worker_started:
            threading.Thread(target=_mlx_worker_main, name="mflux-mlx-worker", daemon=True).start()
            _mlx_worker_started = True
    if not _mlx_worker_ready.wait(timeout=timeout_s):
        raise RuntimeError("mflux MLX worker failed to become ready")
    if _mlx_worker_error:
        raise RuntimeError(
            f"mflux model load failed: {_mlx_worker_error[0]}"
        ) from _mlx_worker_error[0]


def generate_images(prompt: str, width: int, height: int, n: int) -> list[str]:
    """Return list of base64 PNG strings (no data: prefix)."""
    n = max(1, min(int(n), 4))
    if BACKEND == "mock":
        return [_mock_png_b64(width, height, f"{prompt} #{i}") for i in range(n)]

    if BACKEND != "mflux":
        raise RuntimeError(f"Unknown MOOD_BOARD_LOCAL_IMAGE_BACKEND={BACKEND!r} (use mflux|mock)")

    _ensure_mlx_worker()
    result_q: queue.Queue[tuple[str, Any]] = queue.Queue()
    _mlx_jobs.put((result_q, prompt, width, height, n))
    status, payload = result_q.get()
    if status == "err":
        raise payload
    return payload


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    generate_fn: Callable[[str, int, int, int], list[str]] = staticmethod(generate_images)

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        print(f"[mflux-shim] {self.address_string()} {fmt % args}")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path in ("/", "/health", "/v1/health"):
            self._send_json(
                200,
                {
                    "status": "ok",
                    "backend": BACKEND,
                    "model": MODEL_NAME,
                    "quantize": QUANTIZE,
                    "steps": STEPS,
                    "openai_images_path": "/v1/images/generations",
                },
            )
            return
        self._send_json(404, {"error": {"message": f"Not found: {path}", "type": "not_found"}})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        if path != "/v1/images/generations":
            self._send_json(404, {"error": {"message": f"Not found: {path}", "type": "not_found"}})
            return

        length = int(self.headers.get("Content-Length") or 0)
        try:
            req_body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": {"message": "Invalid JSON", "type": "invalid_request"}})
            return

        prompt = (req_body.get("prompt") or "").strip()
        if not prompt:
            self._send_json(
                400, {"error": {"message": "prompt is required", "type": "invalid_request"}}
            )
            return

        n = int(req_body.get("n") or 1)
        width, height = parse_size(req_body.get("size"))

        try:
            images = self.generate_fn(prompt, width, height, n)
        except Exception as exc:  # noqa: BLE001
            self._send_json(
                502,
                {
                    "error": {
                        "message": f"image generation failed: {exc}",
                        "type": "upstream_error",
                    }
                },
            )
            return

        if not images:
            self._send_json(
                502,
                {"error": {"message": "generator returned no images", "type": "upstream_error"}},
            )
            return

        self._send_json(
            200,
            {
                "created": int(time.time()),
                "data": [{"b64_json": img} for img in images[:n]],
            },
        )


def main() -> None:
    if BACKEND == "mflux":
        print(
            f"Loading mflux model={MODEL_NAME!r} quantize={QUANTIZE} "
            "(first run downloads weights via Hugging Face)…"
        )
        try:
            _ensure_mlx_worker()
            print("Model ready.")
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: deferred model load failed at startup: {exc}")
            print("Will retry on first /v1/images/generations request.")

    server = ThreadingHTTPServer((SHIM_HOST, SHIM_PORT), Handler)
    print(
        f"OpenAI images shim listening on http://{SHIM_HOST}:{SHIM_PORT}/v1 "
        f"(backend={BACKEND}, model={MODEL_NAME})"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
