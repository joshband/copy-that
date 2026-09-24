#!/usr/bin/env python3
"""Robotic mood-board + color-extract checks. No UI clicks.

Required (fail the run):
  1. Hermetic generator unit tests (image_slots material, ui, typography).
  2. Frontend composition payload test (focus_type mixed + those slots).
  3. Live API accepts that payload (OpenAPI on the running server).
  4. Non-stream POST /api/v1/colors/extract on test_images/IMG_8324.jpeg;
     every color hex and dominant_colors entry is #RRGGBB.

Optional:
  Live Fal via the OpenAI shim (:8766). Saves images under tmp/mood_board_verify/
  when flux_fast returns. Shim down, connection errors, or billing/credit
  failures are skipped — they do not fail the run. Wrong role/focus_type on
  returned images still fails.

Usage:
  make mood-verify
  .venv/bin/python scripts/mood_board_verify.py
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "test_images" / "IMG_8324.jpeg"
OUT_DIR = ROOT / "tmp" / "mood_board_verify"
API = os.getenv("COPY_THAT_API", "http://127.0.0.1:8000")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
IMAGE_SLOTS = [
    {"focus_type": "material"},
    {"focus_type": "ui"},
    {"focus_type": "typography"},
]
# Fal outage / unpaid account. Not a Copy That schema regression.
_FAL_SKIP_MARKERS = (
    "credit",
    "balance",
    "billing",
    "exhausted",
    "quota",
    "insufficient",
    "payment",
    "402",
    "403",
    "401",
    "forbidden",
    "unauthorized",
    "locked",
    "not listening",
    "connection refused",
    "timed out",
    "timeout",
    "unreachable",
    "failed to connect",
    "nodename nor servname",
)


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


def _redact(text: str, limit: int = 400) -> str:
    secret_keys = ("FAL_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MOOD_BOARD_FLUX_API_KEY")
    cleaned = text
    for name in secret_keys:
        secret = os.getenv(name) or ""
        if secret and secret in cleaned:
            cleaned = cleaned.replace(secret, "[redacted]")
    return cleaned[:limit]


def _json_req(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> tuple[int, dict[str, Any] | list[Any]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")
            parsed: dict[str, Any] | list[Any] = json.loads(body) if body else {}
            return resp.status, parsed
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} → HTTP {exc.code}: {_redact(detail)}") from exc
    except URLError as exc:
        raise RuntimeError(f"{method} {url} → {_redact(str(exc))}") from exc


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )


def _tail(text: str, lines: int = 30) -> str:
    chunk = "\n".join(text.splitlines()[-lines:])
    return _redact(chunk, limit=2000)


def step_hermetic_generator() -> dict[str, Any]:
    python = ROOT / ".venv" / "bin" / "python"
    if not python.is_file():
        python = Path(sys.executable)
    proc = _run(
        [
            str(python),
            "-m",
            "pytest",
            "tests/unit/services/test_mood_board_generator.py",
            "-q",
            "--tb=line",
            "--no-cov",
            "-n0",
            "-k",
            "image_slots or stamps_slot or mixed_focus",
        ],
        cwd=ROOT,
    )
    status = "pass" if proc.returncode == 0 else "fail"
    return {
        "status": status,
        "exit_code": proc.returncode,
        "summary": _tail(proc.stdout + "\n" + proc.stderr, 20),
    }


def step_composition_payload() -> dict[str, Any]:
    proc = _run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "src/components/overview-narrative/__tests__/MoodBoard.composition.test.tsx",
            "--reporter=dot",
        ],
        cwd=ROOT / "frontend",
    )
    status = "pass" if proc.returncode == 0 else "fail"
    return {
        "status": status,
        "exit_code": proc.returncode,
        "summary": _tail(proc.stdout + "\n" + proc.stderr, 25),
    }


def step_api_accepts_mixed() -> dict[str, Any]:
    """Running server schema. Does not enqueue a Celery job."""
    try:
        _status, spec = _json_req("GET", f"{API}/openapi.json", timeout=15)
    except RuntimeError as exc:
        return {"status": "fail", "reason": _redact(str(exc))}
    if not isinstance(spec, dict):
        return {"status": "fail", "reason": "openapi.json was not an object"}
    schemas = (spec.get("components") or {}).get("schemas") or {}
    request = schemas.get("MoodBoardRequest") or {}
    props = request.get("properties") or {}
    focus = (props.get("focus_type") or {}).get("enum") or []
    slots_ok = "image_slots" in props
    image_slot = schemas.get("ImageSlot") or {}
    slot_enum = ((image_slot.get("properties") or {}).get("focus_type") or {}).get("enum") or []
    problems: list[str] = []
    if "mixed" not in focus:
        problems.append(
            "running API MoodBoardRequest.focus_type lacks 'mixed' "
            "(stale uvicorn — restart it, then re-run)"
        )
    if not slots_ok:
        problems.append("running API MoodBoardRequest has no image_slots")
    for needed in ("material", "ui", "typography"):
        if needed not in slot_enum:
            problems.append(f"ImageSlot.focus_type enum missing {needed}")
    if problems:
        return {"status": "fail", "reason": "; ".join(problems), "focus_enum": focus}
    return {
        "status": "pass",
        "focus_enum": focus,
        "image_slots": True,
    }


def _assert_hex_list(values: list[Any], label: str) -> list[str]:
    bad: list[str] = []
    good: list[str] = []
    if not values:
        bad.append(f"{label} empty")
        return bad
    for item in values:
        text = item if isinstance(item, str) else ""
        if HEX_RE.match(text):
            good.append(text)
        else:
            bad.append(f"{label} {text!r}")
    if not good:
        bad.append(f"{label} had no #RRGGBB values")
    return bad


def step_color_extract() -> dict[str, Any]:
    if not FIXTURE.is_file():
        return {"status": "fail", "reason": f"missing fixture {FIXTURE}"}
    try:
        _json_req("GET", f"{API}/health", timeout=5)
    except RuntimeError as exc:
        return {"status": "fail", "reason": f"API not reachable: {_redact(str(exc))}"}

    image_b64 = base64.b64encode(FIXTURE.read_bytes()).decode("ascii")
    try:
        _status, project = _json_req(
            "POST",
            f"{API}/api/v1/projects",
            {
                "name": f"mood-verify-{int(time.time())}",
                "description": "mood-verify color extract",
            },
            timeout=30,
        )
    except RuntimeError as exc:
        return {"status": "fail", "reason": _redact(str(exc))}
    if not isinstance(project, dict):
        return {"status": "fail", "reason": "create project returned a non-object"}
    project_id = project.get("id") or project.get("project_id")
    if not project_id:
        return {"status": "fail", "reason": "create project returned no id"}

    try:
        _status, extracted = _json_req(
            "POST",
            f"{API}/api/v1/colors/extract",
            {
                "image_base64": image_b64,
                "project_id": project_id,
                "max_colors": 6,
                "include_science_artifacts": False,
            },
            timeout=180,
        )
    except RuntimeError as exc:
        return {
            "status": "fail",
            "reason": _redact(str(exc)),
            "project_id": project_id,
        }
    if not isinstance(extracted, dict):
        return {"status": "fail", "reason": "extract response was not an object"}

    colors = extracted.get("colors") or []
    hexes = [c.get("hex") if isinstance(c, dict) else None for c in colors]
    dominant = list(extracted.get("dominant_colors") or [])
    problems = _assert_hex_list(hexes, "colors.hex") + _assert_hex_list(dominant, "dominant_colors")
    oklch_hits = [h for h in hexes + dominant if isinstance(h, str) and "oklch" in h.lower()]
    if oklch_hits:
        problems.append(f"oklch leaked into hex fields: {oklch_hits[:3]}")
    summary = {
        "project_id": project_id,
        "extractor_used": extracted.get("extractor_used"),
        "color_count": len(hexes),
        "hex": [h for h in hexes if isinstance(h, str)],
        "dominant_colors": dominant,
        "fixture": str(FIXTURE.relative_to(ROOT)),
    }
    (OUT_DIR / "color_extract.json").write_text(json.dumps(summary, indent=2))
    if problems:
        summary["status"] = "fail"
        summary["reason"] = "; ".join(problems)
        return summary
    summary["status"] = "pass"
    return summary


def _fal_skip_reason(message: str) -> str | None:
    lowered = message.lower()
    if any(marker in lowered for marker in _FAL_SKIP_MARKERS):
        return _redact(message)
    return None


def _save_image(url: str, dest: Path) -> bool:
    if url.startswith("data:image") and "," in url:
        dest.write_bytes(base64.b64decode(url.split(",", 1)[1]))
        return True
    if url.startswith("http"):
        with urlopen(url, timeout=60) as resp:  # noqa: S310
            dest.write_bytes(resp.read())
        return True
    return False


async def _live_generate() -> list[dict[str, Any]]:
    """Generate the three composition slots from the fixture photograph."""
    sys.path.insert(0, str(ROOT / "src"))
    from copy_that.services.mood_board_generator import (
        MoodBoardGenerator,
        measure_palette_shares,
        resize_reference_jpeg,
    )

    raw = base64.b64encode(FIXTURE.read_bytes()).decode("ascii")
    reference = resize_reference_jpeg(raw)
    colors = measure_palette_shares(
        [
            {"hex": "#D2D5D1", "name": "cream"},
            {"hex": "#3E392D", "name": "dark olive"},
            {"hex": "#FF0000", "name": "red"},
            {"hex": "#C0C0C0", "name": "silver"},
            {"hex": "#D5BD58", "name": "gold"},
            {"hex": "#00CED1", "name": "teal"},
            {"hex": "#F5F5F5", "name": "white smoke"},
        ],
        reference,
    )
    gen = MoodBoardGenerator()
    brief = gen._load_design_brief(reference)
    slots = gen._resolve_image_slots(IMAGE_SLOTS, num_images=3, focus_type="mixed")
    images = await gen._generate_images(
        theme={"name": "Source", "tags": [], "color_palette": []},
        num_images=3,
        focus_type="mixed",
        image_slots=slots,
        policy="fast",
        allow_cloud=True,
        colors=colors,
        design_brief=brief,
        source_image_b64=reference,
    )
    for img in images:
        img["design_brief_subject"] = brief.get("subject")
    return images


def step_live_fal() -> dict[str, Any]:
    flux_base = (os.getenv("MOOD_BOARD_FLUX_BASE_URL") or "http://127.0.0.1:8766/v1").rstrip("/")
    health_url = (
        flux_base[: -len("/v1")] + "/health" if flux_base.endswith("/v1") else flux_base + "/health"
    )
    try:
        _status, health = _json_req("GET", health_url, timeout=5)
    except RuntimeError as exc:
        return {"status": "skipped", "reason": _redact(str(exc))}
    if not isinstance(health, dict) or health.get("status") != "ok":
        return {
            "status": "skipped",
            "reason": f"Fal shim not ready: {_redact(json.dumps(health) if not isinstance(health, dict) else str(health.get('status')))}",
        }

    try:
        images = asyncio.run(_live_generate())
    except Exception as exc:  # noqa: BLE001 — classify billing vs code
        message = _redact(str(exc))
        if _fal_skip_reason(message):
            return {"status": "skipped", "reason": message}
        return {"status": "fail", "reason": message}

    providers = [img.get("provider") for img in images]
    focuses = [img.get("focus_type") for img in images]
    roles = [img.get("role") for img in images]
    expected = ["material", "ui", "typography"]
    if focuses != expected or roles != expected:
        # Collage fallback can still stamp slots. Wrong stamps are a code bug.
        # Missing flux_fast with correct stamps is a Fal skip, not a schema fail.
        if focuses == expected and roles == expected and "flux_fast" not in providers:
            return {
                "status": "skipped",
                "reason": f"flux_fast did not produce images (providers={providers})",
                "focus_type": focuses,
                "role": roles,
            }
        return {
            "status": "fail",
            "reason": f"slot stamps {focuses}/{roles}, expected {expected}",
            "providers": providers,
        }

    if "flux_fast" not in providers:
        return {
            "status": "skipped",
            "reason": f"images stamped correctly but flux_fast was not used (providers={providers})",
            "focus_type": focuses,
            "role": roles,
        }

    saved: list[str] = []
    for index, img in enumerate(images, start=1):
        dest = OUT_DIR / f"fal_slot{index}_{img.get('focus_type')}.png"
        url = str(img.get("url") or "")
        try:
            if _save_image(url, dest):
                saved.append(str(dest.relative_to(ROOT)))
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "fail",
                "reason": f"could not save Fal image {index}: {_redact(str(exc))}",
            }
        meta = {
            "provider": img.get("provider"),
            "focus_type": img.get("focus_type"),
            "role": img.get("role"),
            "selection": img.get("selection"),
            "design_brief_subject": img.get("design_brief_subject"),
        }
        (OUT_DIR / f"fal_slot{index}_{img.get('focus_type')}.meta.json").write_text(
            json.dumps(meta, indent=2)
        )
    return {
        "status": "pass",
        "providers": providers,
        "focus_type": focuses,
        "role": roles,
        "saved": saved,
    }


def _print_step(name: str, result: dict[str, Any]) -> None:
    status = result.get("status")
    extra = result.get("reason") or result.get("summary") or ""
    if result.get("hex"):
        extra = " ".join(result["hex"])
    line = f"  {status}: {name}"
    if extra and status != "pass":
        line += f" — {str(extra).splitlines()[0][:180]}"
    elif status == "pass" and result.get("hex"):
        line += f" — {extra}"
    print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-fal",
        action="store_true",
        help="Do not probe the Fal shim (recorded as skipped)",
    )
    args = parser.parse_args()

    _load_dotenv()
    os.environ.setdefault("MOOD_BOARD_FLUX_BASE_URL", "http://127.0.0.1:8766/v1")
    os.environ.setdefault("MOOD_BOARD_FLUX_API_KEY", "local")
    os.environ.setdefault("MOOD_BOARD_FLUX_MODEL", "flux-schnell")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "steps": {},
    }
    print("=== mood-verify ===")

    print("1) hermetic generator (image_slots)")
    report["steps"]["hermetic_generator"] = step_hermetic_generator()
    _print_step("hermetic_generator", report["steps"]["hermetic_generator"])

    print("2) composition payload (vitest)")
    report["steps"]["composition_payload"] = step_composition_payload()
    _print_step("composition_payload", report["steps"]["composition_payload"])

    print("3) running API accepts focus_type mixed")
    report["steps"]["api_schema"] = step_api_accepts_mixed()
    _print_step("api_schema", report["steps"]["api_schema"])

    print("4) color extract (non-stream) fixture IMG_8324.jpeg")
    report["steps"]["color_extract"] = step_color_extract()
    _print_step("color_extract", report["steps"]["color_extract"])

    print("5) live Fal composition (optional)")
    if args.skip_fal:
        report["steps"]["live_fal"] = {"status": "skipped", "reason": "--skip-fal"}
    else:
        report["steps"]["live_fal"] = step_live_fal()
    _print_step("live_fal", report["steps"]["live_fal"])

    failed = [name for name, step in report["steps"].items() if step.get("status") == "fail"]
    report["ok"] = not failed
    report["failed"] = failed
    report["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    report_path = OUT_DIR / "report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print("=== report ===", report_path)
    if failed:
        print("FAILED:", ", ".join(failed))
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
