from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def _with_label(img: Image.Image, label: str, bar_height: int = 24) -> Image.Image:
    width, height = img.size
    canvas = Image.new("RGB", (width, height + bar_height), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 4), label, fill=(255, 255, 255))
    canvas.paste(img, (0, bar_height))
    return canvas


def _load_rgb(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def _resize_all(images: list[Image.Image]) -> list[Image.Image]:
    widths = [img.width for img in images]
    heights = [img.height for img in images]
    target = (min(widths), min(heights))
    if all(img.size == target for img in images):
        return images
    return [img.resize(target, resample=Image.BILINEAR) for img in images]


def _grid(tiles: list[Image.Image], cols: int) -> Image.Image:
    if not tiles:
        raise ValueError("No tiles provided")
    rows = (len(tiles) + cols - 1) // cols
    widths = [tile.width for tile in tiles]
    heights = [tile.height for tile in tiles]
    tile_w = max(widths)
    tile_h = max(heights)
    canvas = Image.new("RGB", (cols * tile_w, rows * tile_h), (10, 10, 10))
    for idx, tile in enumerate(tiles):
        row = idx // cols
        col = idx % cols
        x = col * tile_w
        y = row * tile_h
        canvas.paste(tile, (x, y))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare depth/normals outputs side-by-side.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image-id", help="Image stem (e.g., IMG_8635)")
    group.add_argument(
        "--all",
        action="store_true",
        help="Generate comparisons for all images found in the output directory",
    )
    parser.add_argument(
        "--output-dir",
        default="test_images_output/geometry",
        help="Directory containing output PNGs",
    )
    parser.add_argument(
        "--input-dir",
        default="test_images",
        help="Directory containing original images",
    )
    parser.add_argument(
        "--label-small",
        default="auto_v2",
        help="Label suffix for small model outputs (default: auto_v2)",
    )
    parser.add_argument(
        "--label-base",
        default="base_v2",
        help="Label suffix for base model outputs (default: base_v2)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output comparison PNG (defaults to <image-id>_compare.png)",
    )

    args = parser.parse_args()
    if args.all and args.output:
        parser.error("--output can only be used with --image-id")
    output_dir = Path(args.output_dir)
    input_dir = Path(args.input_dir)

    def _path(image_id: str, label: str, kind: str) -> Path:
        return output_dir / f"{image_id}_{label}_{kind}.png"

    def _find_original(image_id: str) -> Path | None:
        candidates = [
            input_dir / f"{image_id}{ext}"
            for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"]
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        for path in input_dir.iterdir():
            if path.is_file() and path.stem == image_id:
                return path
        return None

    def _collect_ids() -> list[str]:
        def _ids_for(label: str) -> set[str]:
            suffix = f"_{label}_depth.png"
            ids: set[str] = set()
            for path in output_dir.glob(f"*{suffix}"):
                name = path.name
                if name.endswith(suffix):
                    ids.add(name[: -len(suffix)])
            return ids

        small_ids = _ids_for(args.label_small)
        base_ids = _ids_for(args.label_base)
        return sorted(small_ids & base_ids)

    def _compare_one(image_id: str, output_path: Path | None) -> None:
        original_path = _find_original(image_id)
        if original_path is None:
            raise FileNotFoundError(f"Original image not found for {image_id} in {input_dir}")

        original = _load_rgb(original_path)
        depth_small = _load_rgb(_path(image_id, args.label_small, "depth"))
        depth_base = _load_rgb(_path(image_id, args.label_base, "depth"))
        normals_small = _load_rgb(_path(image_id, args.label_small, "normals"))
        normals_base = _load_rgb(_path(image_id, args.label_base, "normals"))

        original, depth_small, depth_base, normals_small, normals_base = _resize_all(
            [original, depth_small, depth_base, normals_small, normals_base]
        )

        tiles = [
            _with_label(original, "original"),
            _with_label(depth_small, f"depth {args.label_small}"),
            _with_label(depth_base, f"depth {args.label_base}"),
            _with_label(original, "original"),
            _with_label(normals_small, f"normals {args.label_small}"),
            _with_label(normals_base, f"normals {args.label_base}"),
        ]
        grid = _grid(tiles, cols=3)

        resolved_output = output_path or output_dir / f"{image_id}_compare.png"
        grid.save(resolved_output)
        print(f"saved: {resolved_output}")

    if args.all:
        image_ids = _collect_ids()
        if not image_ids:
            raise SystemExit("No matching image outputs found.")
        for image_id in image_ids:
            try:
                _compare_one(image_id, None)
            except FileNotFoundError as exc:
                print(f"skipped: {exc}")
        return

    _compare_one(args.image_id, Path(args.output) if args.output else None)


if __name__ == "__main__":
    main()
