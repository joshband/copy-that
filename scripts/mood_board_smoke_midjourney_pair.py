#!/usr/bin/env python3
"""
Mood-board smoke using a Midjourney 4-up sibling pair.

Default fixtures (same generation, two panels of the 2×2 grid):
  test_images/IMG_8324.jpeg
  test_images/IMG_8325.jpeg

Flow:
  1. Sample a joint palette from both images
  2. Generate themes via MoodBoardGenerator (LM Studio / Anthropic)
  3. Generate images via local mflux shim (:8765) when configured
  4. Write JSON + PNGs under tmp/mood_board_smoke_midjourney_pair/

Requires (local path):
  - LM Studio on MOOD_BOARD_TEXT_BASE_URL (default :1234)
  - scripts/mood_board_local_image_server.py on MOOD_BOARD_IMAGE_BASE_URL (:8765)
  - .env loaded (or env already exported)

Usage:
  set -a && . ./.env && set +a
  python scripts/mood_board_smoke_midjourney_pair.py
  python scripts/mood_board_smoke_midjourney_pair.py --themes-only
  python scripts/mood_board_smoke_midjourney_pair.py \\
    --images test_images/IMG_8324.jpeg test_images/IMG_8325.jpeg
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGES = [
    ROOT / "test_images" / "IMG_8324.jpeg",
    ROOT / "test_images" / "IMG_8325.jpeg",
]
OUT_DIR = ROOT / "tmp" / "mood_board_smoke_midjourney_pair"


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = val.strip().strip('"').strip("'")


def _quantize_hex(rgb: tuple[int, int, int], step: int = 32) -> str:
    r, g, b = (max(0, min(255, (c // step) * step)) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_palette(image_paths: list[Path], max_colors: int = 8) -> list[dict[str, Any]]:
    """Joint palette from Midjourney sibling frames (prefer chromatic accents)."""
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Pillow required: pip install pillow") from exc

    chromatic: Counter[str] = Counter()
    neutrals: Counter[str] = Counter()
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        # Midjourney panels are square; denser sample keeps red/yellow/teal accents.
        sample = img.resize((160, 160), Image.Resampling.BOX)
        for pixel in sample.getdata():
            r, g, b = pixel
            mx, mn = max(r, g, b), min(r, g, b)
            # Skip near-white studio backdrop
            if mn > 220:
                continue
            hex_code = _quantize_hex(pixel, step=24)
            if mx - mn >= 28:
                chromatic[hex_code] += 1
            elif mx < 210:
                neutrals[hex_code] += 1

    ordered = [h for h, _ in chromatic.most_common(max_colors)]
    if len(ordered) < max_colors:
        for h, _ in neutrals.most_common(max_colors - len(ordered)):
            if h not in ordered:
                ordered.append(h)

    if not ordered:
        raise SystemExit("No colors sampled from input images")

    colors: list[dict[str, Any]] = []
    for i, hex_code in enumerate(ordered[:max_colors]):
        colors.append(
            {
                "hex": hex_code,
                "name": f"mj_pair_{i + 1}",
                "temperature": None,
                "saturation_level": None,
                "hue_family": None,
            }
        )
    return colors


def _tcp_ok(url: str, timeout: float = 2.0) -> bool:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    base = f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 80}"
    try:
        with urlopen(Request(base + "/"), timeout=timeout):  # noqa: S310
            return True
    except Exception:
        try:
            # health-style probes
            for path in ("/health", "/v1/models", ""):
                try:
                    with urlopen(Request(base + path, method="GET"), timeout=timeout):  # noqa: S310
                        return True
                except Exception:
                    continue
        except Exception:
            return False
    return False


def check_prereqs(*, themes_only: bool) -> None:
    text_base = (os.getenv("MOOD_BOARD_TEXT_BASE_URL") or "").rstrip("/")
    image_base = (os.getenv("MOOD_BOARD_IMAGE_BASE_URL") or "").rstrip("/")
    missing: list[str] = []
    if not text_base and not os.getenv("ANTHROPIC_API_KEY"):
        missing.append("MOOD_BOARD_TEXT_BASE_URL (LM Studio) or ANTHROPIC_API_KEY")
    elif text_base:
        # LM Studio models endpoint
        try:
            with urlopen(Request(text_base + "/models"), timeout=2.0):  # noqa: S310
                pass
        except Exception:
            missing.append(f"LM Studio not reachable at {text_base} (start Local Server)")
    if not themes_only:
        if not image_base and not os.getenv("OPENAI_API_KEY"):
            missing.append("MOOD_BOARD_IMAGE_BASE_URL (:8765 shim) or OPENAI_API_KEY")
        elif image_base:
            health = image_base.replace("/v1", "") + "/health"
            try:
                with urlopen(Request(health), timeout=2.0) as resp:  # noqa: S310
                    body = resp.read().decode()
                    if '"status": "ok"' not in body and '"status":"ok"' not in body:
                        missing.append(f"image shim unhealthy: {health} → {body[:120]}")
            except Exception:
                missing.append(
                    f"image shim not reachable ({health}); "
                    "run: python scripts/mood_board_local_image_server.py"
                )
    if missing:
        print("Prereqs failed:", file=sys.stderr)
        for item in missing:
            print(f"  - {item}", file=sys.stderr)
        raise SystemExit(1)


def _save_images(variants: list[dict[str, Any]], out_dir: Path) -> list[Path]:
    saved: list[Path] = []
    for vi, variant in enumerate(variants):
        theme = variant.get("theme") or {}
        images = theme.get("generated_images") or []
        for ii, image in enumerate(images):
            url = image.get("url") or ""
            raw: bytes | None = None
            if url.startswith("data:image"):
                b64 = url.split(",", 1)[-1]
                raw = base64.b64decode(b64)
            elif url.startswith("http"):
                with urlopen(Request(url), timeout=60) as resp:  # noqa: S310
                    raw = resp.read()
            elif image.get("b64_json"):
                raw = base64.b64decode(image["b64_json"])
            if not raw:
                # Generator stores OpenAI-style url; local shim may return b64 in url field differently
                continue
            path = out_dir / f"variant{vi + 1}_img{ii + 1}.png"
            path.write_bytes(raw)
            saved.append(path)
    return saved


async def _run(args: argparse.Namespace) -> int:
    _load_dotenv()
    check_prereqs(themes_only=args.themes_only)

    images = [Path(p).resolve() for p in args.images]
    for path in images:
        if not path.is_file():
            raise SystemExit(f"Missing image: {path}")

    colors = extract_palette(images, max_colors=args.max_colors)
    print(f"Palette ({len(colors)} from {len(images)} Midjourney siblings):")
    for c in colors:
        print(f"  {c['hex']}  {c['name']}")

    # Import after dotenv so generator sees env
    sys.path.insert(0, str(ROOT / "src"))
    from copy_that.services.mood_board_generator import MoodBoardGenerator

    gen = MoodBoardGenerator()
    t0 = time.time()
    result = await gen.generate(
        colors=colors,
        num_variants=args.num_variants,
        include_images=not args.themes_only,
        num_images_per_variant=args.num_images,
        focus_type=args.focus_type,
    )
    elapsed = time.time() - t0

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "source_images": [str(p) for p in images],
        "note": "IMG_8324 + IMG_8325 are sibling panels from the same Midjourney 4-up generation",
        "palette": colors,
        "result": result,
        "elapsed_s": round(elapsed, 2),
    }
    (out_dir / "result.json").write_text(json.dumps(meta, indent=2))
    saved = _save_images(result.get("variants") or [], out_dir)

    print(f"\nDone in {elapsed:.1f}s → {out_dir}")
    print(f"models: {result.get('models_used')}")
    for v in result.get("variants") or []:
        print(f"  • {v.get('title')}: {v.get('subtitle')} | vibe={v.get('vibe')}")
    if saved:
        print(f"saved {len(saved)} PNG(s)")
    elif not args.themes_only:
        print("warning: no PNGs decoded (check image provider response shape)", file=sys.stderr)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--images",
        nargs="+",
        default=[str(p) for p in DEFAULT_IMAGES],
        help="Midjourney sibling frames (default: IMG_8324 + IMG_8325)",
    )
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    parser.add_argument("--num-variants", type=int, default=2)
    parser.add_argument(
        "--num-images", type=int, default=2, help="Images per variant (smoke default 2)"
    )
    parser.add_argument("--max-colors", type=int, default=8)
    parser.add_argument("--focus-type", choices=("material", "typography"), default="material")
    parser.add_argument("--themes-only", action="store_true")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
