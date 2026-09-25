#!/usr/bin/env python3
"""
OpenAI Images API shim backed by Fal.ai FLUX.1 [schnell].

Copy That mood board ``flux_fast`` expects OpenAI ``images.generate``:
  POST /v1/images/generations
  { "model", "prompt", "n", "size" }
  → { "created": …, "data": [ { "url" } | { "b64_json" } ] }

Fal's native API is NOT OpenAI-shaped. This shim translates:

  OpenAI request  →  POST https://fal.run/fal-ai/flux/schnell
  Authorization: Key $FAL_KEY

Usage:
  # 1. Get a key: https://fal.ai/dashboard/keys
  export FAL_KEY=…
  python scripts/mood_board_fal_openai_shim.py

  # 2. In Copy That .env (do not commit secrets):
  MOOD_BOARD_FLUX_BASE_URL=http://127.0.0.1:8766/v1
  MOOD_BOARD_FLUX_API_KEY=local
  MOOD_BOARD_FLUX_MODEL=flux-schnell
  FAL_KEY=…   # also read by the shim process

  # 3. Restart API + celery; confirm health lists flux_fast

Env:
  SHIM_HOST / SHIM_PORT                 default 127.0.0.1:8766
  FAL_KEY                               required
  FAL_FLUX_ENDPOINT                     default fal-ai/flux/schnell
  FAL_FLUX_STYLE_ENDPOINT               default fal-ai/flux-pro/v1.1-ultra/redux
  FAL_FLUX_STYLE_STRENGTH               default 0.02
  FAL_NUM_INFERENCE_STEPS               default 4
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

SHIM_HOST = os.getenv("SHIM_HOST", "127.0.0.1")
SHIM_PORT = int(os.getenv("SHIM_PORT", "8766"))
FAL_KEY = (os.getenv("FAL_KEY") or os.getenv("MOOD_BOARD_FLUX_API_KEY") or "").strip()
FAL_ENDPOINT = (os.getenv("FAL_FLUX_ENDPOINT") or "fal-ai/flux/schnell").strip()
# flux/dev/redux ignores a caller prompt. flux-pro/v1.1/redux accepts one but
# has no style weight, so the photo is redrawn. Ultra Redux takes the prompt
# and image_prompt_strength. 0.18 redraws the product. 0.06 still holds a
# device on the UI slot. 0.02 lets the layout prompt set the board; enamel
# is thinner at that weight.
FAL_STYLE_ENDPOINT = (
    os.getenv("FAL_FLUX_STYLE_ENDPOINT") or "fal-ai/flux-pro/v1.1-ultra/redux"
).strip()
FAL_STYLE_STRENGTH = float(os.getenv("FAL_FLUX_STYLE_STRENGTH", "0.02"))
FAL_STEPS = int(os.getenv("FAL_NUM_INFERENCE_STEPS", "4"))
FAL_RUN_URL = f"https://fal.run/{FAL_ENDPOINT.lstrip('/')}"
FAL_STYLE_URL = f"https://fal.run/{FAL_STYLE_ENDPOINT.lstrip('/')}"


def parse_size(size: str | None) -> dict[str, int]:
    """Map OpenAI WxH to Fal image_size object."""
    if not size:
        return {"width": 1024, "height": 1024}
    try:
        w_s, h_s = str(size).lower().split("x", 1)
        w, h = int(w_s), int(h_s)
        w = max(256, min(1440, w))
        h = max(256, min(1440, h))
        return {"width": w, "height": h}
    except (ValueError, AttributeError):
        return {"width": 1024, "height": 1024}


def fal_generate(
    *,
    prompt: str,
    size: str | None,
    n: int,
    image: str | None = None,
    strength: float | None = None,
) -> list[dict[str, str]]:
    """Call Fal sync run; return OpenAI-style data items.

    A source image is a style reference (FLUX Redux), not an image-to-image
    init. Text-only requests stay on FLUX schnell.
    """
    del strength
    if not FAL_KEY:
        raise RuntimeError("FAL_KEY (or MOOD_BOARD_FLUX_API_KEY) is not set")

    if image:
        image_url = image if image.startswith(("http://", "https://", "data:")) else (
            f"data:image/jpeg;base64,{image}"
        )
        payload: dict[str, Any] = {
            "prompt": prompt,
            "image_url": image_url,
            "image_prompt_strength": FAL_STYLE_STRENGTH,
            "num_images": 1,
            "enable_safety_checker": True,
            "output_format": "png",
            "aspect_ratio": "1:1",
        }
        run_url = FAL_STYLE_URL
    else:
        payload = {
            "prompt": prompt,
            "num_images": max(1, min(4, n)),
            "num_inference_steps": FAL_STEPS,
            "image_size": parse_size(size),
            "enable_safety_checker": True,
            "output_format": "png",
        }
        run_url = FAL_RUN_URL
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        run_url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Key {FAL_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"Fal HTTP {exc.code}: {detail}") from exc

    images = raw.get("images") or []
    out: list[dict[str, str]] = []
    for img in images:
        if not isinstance(img, dict):
            continue
        url = img.get("url")
        if isinstance(url, str) and url.startswith("data:"):
            # data:image/png;base64,…
            try:
                b64 = url.split(",", 1)[1]
                out.append({"b64_json": b64})
            except IndexError:
                out.append({"url": url})
        elif isinstance(url, str) and url:
            out.append({"url": url})
    if not out:
        raise RuntimeError(f"Fal returned no images: {json.dumps(raw)[:400]}")
    return out


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[fal-shim] {self.address_string()} - {fmt % args}")

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in {"/health", "/v1/health"}:
            self._send_json(
                200,
                {
                    "status": "ok" if FAL_KEY else "missing_fal_key",
                    "backend": "fal",
                    "endpoint": FAL_ENDPOINT,
                    "style_endpoint": FAL_STYLE_ENDPOINT,
                    "openai_images_path": "/v1/images/generations",
                },
            )
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path not in {"/v1/images/generations", "/images/generations"}:
            self._send_json(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8") if length else "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": {"message": "invalid JSON"}})
            return

        prompt = (body.get("prompt") or "").strip()
        if not prompt:
            self._send_json(400, {"error": {"message": "prompt is required"}})
            return
        n = int(body.get("n") or 1)
        size = body.get("size")
        image = body.get("image")
        strength = body.get("strength")

        try:
            data = fal_generate(
                prompt=prompt,
                size=size,
                n=n,
                image=image if isinstance(image, str) else None,
                strength=float(strength) if isinstance(strength, (int, float)) else None,
            )
        except Exception as exc:
            self._send_json(502, {"error": {"message": str(exc)}})
            return

        self._send_json(200, {"created": int(time.time()), "data": data})


def main() -> None:
    if not FAL_KEY:
        print("ERROR: set FAL_KEY (https://fal.ai/dashboard/keys) before starting.")
        raise SystemExit(1)
    server = ThreadingHTTPServer((SHIM_HOST, SHIM_PORT), Handler)
    print(
        f"Fal→OpenAI images shim on http://{SHIM_HOST}:{SHIM_PORT}/v1 "
        f"(endpoint={FAL_ENDPOINT})"
    )
    print(f"Point MOOD_BOARD_FLUX_BASE_URL=http://{SHIM_HOST}:{SHIM_PORT}/v1")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
