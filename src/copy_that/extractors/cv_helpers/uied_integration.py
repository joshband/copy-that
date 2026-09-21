"""
UIED integration (optional, best-effort).

Runs an external UIED runner script (UIED_RUNNER env) against an image path and returns
token-like dicts. If unavailable or failing, degrades gracefully.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from typing import Any

from PIL import Image

logger = logging.getLogger(__name__)


def run_uied(image: Image.Image | str, timeout: int = 20) -> list[dict[str, Any]]:
    """
    Invoke external UIED runner and parse tokens.

    Requirements:
    - UIED_RUNNER env pointing to a script/binary that accepts an image path and emits JSON to stdout.
      Expected JSON schema: {"elements": [{"bounds": [x1,y1,x2,y2], "type": "...", "text": "..."}]}
    """
    runner = os.getenv("UIED_RUNNER")
    enabled_env = os.getenv("ENABLE_UIED", "1")
    enabled = enabled_env not in {"0", "false", "False"}
    if not enabled or not runner:
        return []

    tmp_path: str | None = None
    try:
        if isinstance(image, Image.Image):
            fd, tmp_path = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            image.save(tmp_path)
        else:
            tmp_path = image

        cmd = [runner, tmp_path]
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        if result.returncode != 0:
            logger.warning(
                "UIED runner failed (%s): %s",
                result.returncode,
                result.stderr.decode("utf-8", "ignore"),
            )
            return []
        payload = result.stdout.decode("utf-8", "ignore")
        data = json.loads(payload)
    except Exception as exc:  # pragma: no cover - external invocation
        logger.warning("UIED integration skipped: %s", exc)
        return []
    finally:
        if isinstance(image, Image.Image) and tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    elements = data.get("elements") if isinstance(data, dict) else None
    if not isinstance(elements, list):
        return []

    tokens: list[dict[str, Any]] = []
    for idx, el in enumerate(elements):
        bounds = el.get("bounds") or el.get("bbox")
        if not bounds or len(bounds) != 4:
            continue
        x1, y1, x2, y2 = bounds
        bbox = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
        tokens.append(
            {
                "id": el.get("id") or f"uied-{idx + 1}",
                "bbox": bbox,
                "type": el.get("type") or el.get("label") or "component",
                "text": el.get("text"),
                "uied_label": el.get("type") or el.get("label"),
                "source": "uied",
            }
        )
    return tokens
