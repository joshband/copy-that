#!/usr/bin/env python3
"""
Minimal OpenAI Images API shim for Automatic1111 / Forge txt2img.

Copy That mood board expects OpenAI-compatible:
  POST /v1/images/generations
  { "model", "prompt", "n", "size" }
  → { "data": [ { "b64_json": "..." } ] }

LM Studio typically does NOT serve image generation for chat models.
On Apple Silicon, prefer the primary shim:
  scripts/mood_board_local_image_server.py  (mflux FLUX.1-schnell)

This A1111/Forge shim is a footnote for users who already run WebUI.
Usage:
  # Start A1111/Forge with --api (default http://127.0.0.1:7860)
  python scripts/mood_board_a1111_openai_shim.py

  # Or:
  A1111_BASE_URL=http://127.0.0.1:7860 SHIM_PORT=8765 \\
    python scripts/mood_board_a1111_openai_shim.py

Then in .env:
  MOOD_BOARD_IMAGE_BASE_URL=http://127.0.0.1:8765/v1
  MOOD_BOARD_IMAGE_API_KEY=local
  MOOD_BOARD_IMAGE_MODEL=local-sd

Smoke test:
  curl -s http://127.0.0.1:8765/v1/images/generations \\
    -H 'Content-Type: application/json' \\
    -d '{"model":"local-sd","prompt":"brushed aluminum knob","n":1,"size":"512x512"}' \\
    | python -c "import sys,json; d=json.load(sys.stdin); print('ok', len(d['data'][0]['b64_json']))"

Dependencies: only the Python stdlib (urllib). No FastAPI required.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

A1111_BASE_URL = (os.getenv("A1111_BASE_URL") or "http://127.0.0.1:7860").rstrip("/")
SHIM_HOST = os.getenv("SHIM_HOST", "127.0.0.1")
SHIM_PORT = int(os.getenv("SHIM_PORT", "8765"))
DEFAULT_STEPS = int(os.getenv("A1111_STEPS", "20"))
DEFAULT_CFG = float(os.getenv("A1111_CFG_SCALE", "7"))


def _parse_size(size: str | None) -> tuple[int, int]:
    if not size:
        return 512, 512
    match = re.fullmatch(r"(\d+)x(\d+)", size.strip())
    if not match:
        return 512, 512
    w, h = int(match.group(1)), int(match.group(2))
    # A1111 prefers multiples of 64; clamp to a sane local range
    w = max(256, min(1024, (w // 64) * 64))
    h = max(256, min(1024, (h // 64) * 64))
    return w or 512, h or 512


def _a1111_txt2img(prompt: str, width: int, height: int, n: int) -> list[str]:
    payload = {
        "prompt": prompt,
        "negative_prompt": "blurry, low quality, watermark, text artifacts",
        "steps": DEFAULT_STEPS,
        "cfg_scale": DEFAULT_CFG,
        "width": width,
        "height": height,
        "batch_size": max(1, min(n, 4)),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{A1111_BASE_URL}/sdapi/v1/txt2img",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    images = data.get("images") or []
    if not isinstance(images, list):
        return []
    return [img for img in images if isinstance(img, str)]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        print(f"[a1111-shim] {self.address_string()} {fmt % args}")

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
                    "a1111_base_url": A1111_BASE_URL,
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
        width, height = _parse_size(req_body.get("size"))

        try:
            images = _a1111_txt2img(prompt, width, height, n)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            self._send_json(
                502,
                {
                    "error": {
                        "message": f"A1111 HTTP {exc.code}: {detail}",
                        "type": "upstream_error",
                    }
                },
            )
            return
        except Exception as exc:  # noqa: BLE001
            self._send_json(
                502,
                {"error": {"message": f"A1111 request failed: {exc}", "type": "upstream_error"}},
            )
            return

        if not images:
            self._send_json(
                502,
                {"error": {"message": "A1111 returned no images", "type": "upstream_error"}},
            )
            return

        self._send_json(
            200,
            {
                "created": 0,
                "data": [{"b64_json": img} for img in images[:n]],
            },
        )


def main() -> None:
    server = ThreadingHTTPServer((SHIM_HOST, SHIM_PORT), Handler)
    print(
        f"OpenAI images shim listening on http://{SHIM_HOST}:{SHIM_PORT}/v1 "
        f"(A1111={A1111_BASE_URL})"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
