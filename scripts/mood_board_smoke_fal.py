#!/usr/bin/env python3
"""
Robotic Fal Flux smoke using fixtures under test_images/.

Default: Midjourney sibling pair IMG_8324 + IMG_8325 (same as local mflux smoke).

Flow:
  1. Sample joint palette from input images
  2. Assert Fal OpenAI shim (:8766) healthy + flux_fast in registry
  3. MoodBoardGenerator themes + imagery (policy=balanced → prefers flux_fast)
  4. Optional live HTTP: create project → color extract → gradient → guide-pack
  5. Write artifacts under tmp/mood_board_smoke_fal/

Usage:
  set -a && . ./.env && set +a
  # Fal shim: make fal-flux-shim   (or scripts/dev_labs.sh --no-vite)
  python scripts/mood_board_smoke_fal.py
  python scripts/mood_board_smoke_fal.py --images test_images/IMG_8405.jpeg
  python scripts/mood_board_smoke_fal.py --skip-http
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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGES = [
    ROOT / "test_images" / "IMG_8324.jpeg",
    ROOT / "test_images" / "IMG_8325.jpeg",
]
OUT_DIR = ROOT / "tmp" / "mood_board_smoke_fal"
API = os.getenv("COPY_THAT_API", "http://127.0.0.1:8000")


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


def _quantize_hex(rgb: tuple[int, int, int], step: int = 24) -> str:
    r, g, b = (max(0, min(255, (c // step) * step)) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_palette(image_paths: list[Path], max_colors: int = 8) -> list[dict[str, Any]]:
    from PIL import Image

    chromatic: Counter[str] = Counter()
    neutrals: Counter[str] = Counter()
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        sample = img.resize((160, 160), Image.Resampling.BOX)
        for pixel in sample.getdata():
            r, g, b = pixel
            mx, mn = max(r, g, b), min(r, g, b)
            if mn > 220:
                continue
            hex_code = _quantize_hex(pixel)
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
        raise SystemExit(f"No colors sampled from {[str(p) for p in image_paths]}")

    return [
        {
            "hex": hex_code,
            "name": f"fixture_{i + 1}",
            "temperature": None,
            "saturation_level": None,
            "hue_family": None,
        }
        for i, hex_code in enumerate(ordered[:max_colors])
    ]


def _json_req(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 120.0,
) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"{method} {url} → HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"{method} {url} → {exc}") from exc


def assert_fal_ready() -> dict[str, Any]:
    flux_base = (os.getenv("MOOD_BOARD_FLUX_BASE_URL") or "").rstrip("/")
    if not flux_base:
        raise SystemExit("MOOD_BOARD_FLUX_BASE_URL unset — expected http://127.0.0.1:8766/v1")
    if not os.getenv("FAL_KEY"):
        raise SystemExit("FAL_KEY unset")

    health = _json_req("GET", flux_base.replace("/v1", "") + "/health", timeout=5)
    if health.get("status") != "ok":
        raise SystemExit(f"Fal shim unhealthy: {health}")

    # Direct OpenAI-shaped smoke (small)
    gen = _json_req(
        "POST",
        flux_base + "/images/generations",
        {
            "model": os.getenv("MOOD_BOARD_FLUX_MODEL") or "flux-schnell",
            "prompt": "robotic smoke: brushed aluminum knob, soft light",
            "n": 1,
            "size": "512x512",
        },
        timeout=120,
    )
    if not gen.get("data"):
        raise SystemExit(f"Fal shim images.generate empty: {gen}")

    sys.path.insert(0, str(ROOT / "src"))
    from copy_that.services.mood_board_images.registry import health_snapshot

    snap = health_snapshot()
    ids = [b["id"] for b in snap["backends"]]
    if "flux_fast" not in ids:
        raise SystemExit(f"flux_fast missing from registry: {ids}")
    return {"shim_health": health, "registry": snap, "direct_gen_keys": list(gen["data"][0].keys())}


def save_generated_images(result: dict[str, Any], out: Path) -> list[Path]:
    saved: list[Path] = []
    for vi, variant in enumerate(result.get("variants") or []):
        theme = variant.get("theme") or {}
        for ii, img in enumerate(theme.get("generated_images") or []):
            dest = out / f"variant{vi + 1}_img{ii + 1}.png"
            url = img.get("url") or ""
            if url.startswith("data:image") and "," in url:
                dest.write_bytes(base64.b64decode(url.split(",", 1)[1]))
            elif url.startswith("http"):
                with urlopen(url, timeout=60) as resp:  # noqa: S310
                    dest.write_bytes(resp.read())
            else:
                continue
            meta = {
                "provider": img.get("provider"),
                "selection": img.get("selection"),
                "prompt": (img.get("prompt") or "")[:240],
            }
            (out / f"variant{vi + 1}_img{ii + 1}.meta.json").write_text(json.dumps(meta, indent=2))
            saved.append(dest)
    return saved


async def run_generator(colors: list[dict[str, Any]], *, num_images: int) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "src"))
    from copy_that.services.mood_board_generator import MoodBoardGenerator

    gen = MoodBoardGenerator()
    return await gen.generate(
        colors=colors,
        num_variants=2,
        include_images=True,
        num_images_per_variant=num_images,
        focus_type="material",
        policy="balanced",
        allow_cloud=True,
        max_latency_ms=180_000,
    )


def _sse_extract_colors(image_base64: str, project_id: int, *, max_colors: int = 8) -> dict[str, Any]:
    """Use extract-streaming (non-stream /colors/extract can fail on oklch hex from CV)."""
    payload = json.dumps(
        {
            "image_base64": image_base64,
            "project_id": project_id,
            "max_colors": max_colors,
        }
    ).encode("utf-8")
    req = Request(
        f"{API}/api/v1/colors/extract-streaming",
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        method="POST",
    )
    events: list[dict[str, Any]] = []
    with urlopen(req, timeout=180) as resp:  # noqa: S310
        for raw in resp.read().decode("utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line.startswith("data:"):
                continue
            chunk = line[5:].strip()
            if not chunk or chunk == "[DONE]":
                continue
            try:
                events.append(json.loads(chunk))
            except json.JSONDecodeError:
                continue
    if any(isinstance(e, dict) and e.get("error") for e in events):
        err = next(e for e in events if e.get("error"))
        raise RuntimeError(f"colors extract-streaming error: {err.get('error')}")
    final = next((e for e in reversed(events) if e.get("colors") or e.get("color_count")), None)
    return {"events": len(events), "final": final or {}, "raw_tail": events[-3:] if events else []}


def run_http_pipeline(image_path: Path, out: Path) -> dict[str, Any]:
    """Live API: project → colors → gradients → guide-pack (+ optional mood job enqueue)."""
    b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    media = "image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"

    project = _json_req(
        "POST",
        f"{API}/api/v1/projects",
        {"name": f"fal-smoke-{image_path.stem}", "description": "robotic Fal smoke"},
        timeout=30,
    )
    project_id = project.get("id") or project.get("project_id")
    if not project_id:
        raise RuntimeError(f"create project failed: {project}")

    stream_info = _sse_extract_colors(b64, int(project_id), max_colors=8)
    # Prefer persisted project colors (hex) over stream payload quirks
    stored = _json_req("GET", f"{API}/api/v1/projects/{project_id}/colors", timeout=30)
    if isinstance(stored, list):
        color_list = [c for c in stored if isinstance(c, dict) and str(c.get("hex", "")).startswith("#")]
    else:
        color_list = []
    colors = {"colors": color_list, "stream": stream_info}
    grads = _json_req(
        "POST",
        f"{API}/api/v1/gradients/extract",
        {
            "image_base64": b64,
            "image_media_type": media,
            "project_id": project_id,
        },
        timeout=120,
    )
    guide = _json_req(
        "GET",
        f"{API}/api/v1/design-tokens/export/guide-pack?project_id={project_id}",
        timeout=60,
    )
    html = urlopen(  # noqa: S310
        Request(f"{API}/api/v1/design-tokens/export/guide-html?project_id={project_id}"),
        timeout=60,
    ).read()
    (out / "guide.html").write_bytes(html)

    mb_health = _json_req("GET", f"{API}/api/v1/mood-board/health", timeout=10)

    # Enqueue themes+imagery (Celery) — poll briefly
    color_rows = []
    for c in (colors.get("colors") or colors.get("tokens") or [])[:8]:
        if isinstance(c, dict) and c.get("hex"):
            color_rows.append({"hex": c["hex"], "name": c.get("name")})
    job_info = None
    job_result = None
    if color_rows:
        try:
            job_info = _json_req(
                "POST",
                f"{API}/api/v1/mood-board/generate",
                {
                    "colors": color_rows,
                    "num_variants": 2,
                    "include_images": True,
                    "num_images_per_variant": 1,
                    "focus_type": "material",
                    "policy": "balanced",
                    "allow_cloud": True,
                },
                timeout=30,
            )
            job_id = job_info.get("job_id")
            deadline = time.time() + 180
            while time.time() < deadline and job_id:
                status = _json_req("GET", f"{API}/api/v1/jobs/{job_id}", timeout=15)
                st = status.get("status")
                if st in {"completed", "failed"}:
                    job_result = status
                    break
                time.sleep(2)
        except Exception as exc:
            job_info = {"error": str(exc)}

    return {
        "project_id": project_id,
        "color_count": len(colors.get("colors") or colors.get("tokens") or []),
        "gradient_count": len(grads.get("tokens") or grads.get("gradients") or []),
        "guide_pack_title": (guide.get("meta") or {}).get("title"),
        "guide_html_bytes": len(html),
        "mood_board_health_backends": [
            (b.get("id"), b.get("available")) for b in (mb_health.get("backends") or [])
        ],
        "mood_job": job_info,
        "mood_job_result_status": (job_result or {}).get("status"),
        "mood_job_models": ((job_result or {}).get("result") or {}).get("models_used"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--images",
        nargs="+",
        type=Path,
        default=DEFAULT_IMAGES,
        help="Fixture images (default: Midjourney pair 8324/8325)",
    )
    parser.add_argument("--num-images", type=int, default=1, help="Images per variant")
    parser.add_argument("--skip-http", action="store_true", help="Skip live API pipeline")
    parser.add_argument("--skip-generator", action="store_true", help="Skip in-process generator")
    args = parser.parse_args()

    _load_dotenv()
    # Prefer Flux URL for this smoke
    os.environ.setdefault("MOOD_BOARD_FLUX_BASE_URL", "http://127.0.0.1:8766/v1")
    os.environ.setdefault("MOOD_BOARD_FLUX_API_KEY", "local")
    os.environ.setdefault("MOOD_BOARD_FLUX_MODEL", "flux-schnell")
    os.environ.setdefault("MOOD_BOARD_ROUTING_POLICY", "balanced")

    images = [p if p.is_absolute() else ROOT / p for p in args.images]
    for p in images:
        if not p.is_file():
            raise SystemExit(f"Missing image: {p}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "images": [str(p.relative_to(ROOT)) for p in images],
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    print("=== 1) Fal / flux_fast readiness ===")
    report["fal"] = assert_fal_ready()
    print("  OK shim + flux_fast", report["fal"]["direct_gen_keys"])

    print("=== 2) Palette from fixtures ===")
    colors = extract_palette(images)
    report["palette"] = colors
    (OUT_DIR / "palette.json").write_text(json.dumps(colors, indent=2))
    print("  colors:", [c["hex"] for c in colors])

    if not args.skip_generator:
        print("=== 3) MoodBoardGenerator (balanced → Fal) ===")
        t0 = time.time()
        result = asyncio.run(run_generator(colors, num_images=args.num_images))
        elapsed = round(time.time() - t0, 2)
        (OUT_DIR / "generator_result.json").write_text(json.dumps(result, indent=2)[:200_000])
        saved = save_generated_images(result, OUT_DIR)
        providers = []
        for v in result.get("variants") or []:
            for img in (v.get("theme") or {}).get("generated_images") or []:
                providers.append((img.get("provider"), (img.get("selection") or {}).get("provider")))
        report["generator"] = {
            "elapsed_s": elapsed,
            "models_used": result.get("models_used"),
            "providers": providers,
            "saved": [str(p.relative_to(ROOT)) for p in saved],
        }
        print("  models_used:", result.get("models_used"))
        print("  providers:", providers)
        print("  saved:", report["generator"]["saved"])
        if not any(p[0] == "flux_fast" or p[1] == "flux_fast" for p in providers):
            print("  WARN: expected flux_fast provider — check fallback chain")

    if not args.skip_http:
        print("=== 4) Live HTTP pipeline ===")
        try:
            report["http"] = run_http_pipeline(images[0], OUT_DIR)
            print("  project", report["http"].get("project_id"))
            print("  colors/grads", report["http"].get("color_count"), report["http"].get("gradient_count"))
            print("  backends", report["http"].get("mood_board_health_backends"))
            print("  mood job", report["http"].get("mood_job_result_status"), report["http"].get("mood_job_models"))
        except Exception as exc:
            report["http"] = {"error": str(exc)}
            print("  HTTP pipeline error:", exc)

    report["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUT_DIR / "report.json").write_text(json.dumps(report, indent=2))
    print("=== DONE ===", OUT_DIR / "report.json")


if __name__ == "__main__":
    main()
