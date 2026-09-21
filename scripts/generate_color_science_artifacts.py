#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from copy_that.application.cv.color_cv_extractor import CVColorExtractor

    from copy_that.application.color_science_artifacts import build_color_science_artifacts
except Exception as exc:  # pragma: no cover - CLI guard
    raise SystemExit(f"Failed to import extraction modules: {exc}")


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _slugify(name: str) -> str:
    safe = []
    for ch in name:
        if ch.isalnum():
            safe.append(ch.lower())
        elif ch in {"-", "_"}:
            safe.append(ch)
        else:
            safe.append("_")
    slug = "".join(safe).strip("_")
    return slug or "image"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _write_base64_image(path: Path, data: str) -> None:
    path.write_bytes(base64.b64decode(data))


def _collect_images(paths: list[str], directory: str | None, limit: int | None) -> list[Path]:
    images: list[Path] = []
    if directory:
        root = Path(directory)
        if root.exists():
            images.extend(
                sorted([p for p in root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES])
            )
    images.extend(Path(p) for p in paths)
    images = [p for p in images if p.exists() and p.suffix.lower() in IMAGE_SUFFIXES]
    if limit is not None:
        images = images[:limit]
    return images


def _export_result(image_path: Path, out_root: Path, max_colors: int, copy_input: bool) -> Path:
    extractor = CVColorExtractor(max_colors=max_colors, use_superpixels=True, debug_artifacts=False)
    data = image_path.read_bytes()
    result = extractor.extract_from_bytes(data)

    slug = _slugify(image_path.stem)
    out_dir = out_root / slug
    images_dir = out_dir / "images"
    json_dir = out_dir / "json"
    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    if copy_input:
        shutil.copy2(image_path, out_dir / image_path.name)

    artifacts = build_color_science_artifacts(result.colors, max_colors=max_colors)
    manifest = {
        "source_image": str(image_path),
        "output_dir": str(out_dir),
        "artifacts": {"images": [], "json": []},
    }

    for idx, item in enumerate(artifacts.images, start=1):
        filename = f"{idx:02d}_{item['type']}.png"
        rel_path = Path("images") / filename
        _write_base64_image(images_dir / filename, item["base64"])
        manifest["artifacts"]["images"].append(
            {
                "type": item["type"],
                "description": item.get("description"),
                "file": str(rel_path),
            }
        )

    for idx, item in enumerate(artifacts.json, start=1):
        filename = f"{idx:02d}_{item['type']}.json"
        rel_path = Path("json") / filename
        _write_json(json_dir / filename, item["payload"])
        manifest["artifacts"]["json"].append(
            {
                "type": item["type"],
                "file": str(rel_path),
            }
        )

    _write_json(out_dir / "manifest.json", manifest)
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate color science artifacts")
    parser.add_argument("images", nargs="*", help="Image paths to process")
    parser.add_argument("--dir", dest="directory", help="Directory to scan for images")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of images")
    parser.add_argument("--out-dir", default="storage/color_science_artifacts", help="Output root")
    parser.add_argument("--max-colors", type=int, default=10, help="Max colors to extract")
    parser.add_argument("--copy-input", action="store_true", help="Copy input images")

    args = parser.parse_args()
    images = _collect_images(args.images, args.directory, args.limit)
    if not images:
        raise SystemExit("No images found to process")

    out_root = Path(args.out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    outputs = []
    for image_path in images:
        outputs.append(_export_result(image_path, out_root, args.max_colors, args.copy_input))

    _write_json(out_root / "index.json", {"outputs": [str(p) for p in outputs]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
