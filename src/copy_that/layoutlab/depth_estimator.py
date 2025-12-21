"""Depth estimation helpers to refine spacing classification."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - optional deps
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]

DepthMap = Any


def estimate_depth_map(image: Any) -> DepthMap | None:
    """
    Produce a lightweight relative depth map.

    Prefers MiDaS if installed, otherwise falls back to Laplacian variance over grayscale.
    """
    if np is None:
        return None
    gray: Any
    if isinstance(image, np.ndarray):
        if image.ndim == 2:
            gray = image
        else:
            gray = image[..., 0]
    else:
        try:
            from PIL import Image

            if isinstance(image, Image.Image):
                gray = np.array(image.convert("L"))
            else:
                return None
        except Exception:
            return None

    # Optional MiDaS path
    try:
        import torch  # type: ignore
        from torchvision.models.midas import Midas3_0SmallWeights, midas_v3_0_small  # type: ignore
        from torchvision.transforms import Compose, Normalize, Resize, ToTensor  # type: ignore
    except Exception:
        torch = None  # type: ignore
    if cv2 is not None and torch is not None:  # pragma: no cover - heavy deps
        try:
            weights = Midas3_0SmallWeights.DEFAULT
            model = midas_v3_0_small(weights=weights).to("cpu").eval()
            transform = Compose(
                [
                    Resize((256, 256)),
                    ToTensor(),
                    Normalize(mean=weights.meta["mean"], std=weights.meta["std"]),
                ]
            )
            tensor = transform(gray).unsqueeze(0)
            with torch.no_grad():
                prediction = model(tensor)
            resized = cv2.resize(
                prediction.squeeze().cpu().numpy(),
                (gray.shape[1], gray.shape[0]),
                interpolation=cv2.INTER_CUBIC,
            )
            depth = resized.astype("float32")
            depth = depth - depth.min()
            if depth.max() > 0:
                depth = depth / depth.max()
            return depth
        except Exception:
            pass

    # CPU fallback: local contrast as pseudo-depth
    if cv2 is None:
        return gray.astype("float32") / float(gray.max() or 1)
    lap = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    depth = cv2.GaussianBlur(abs(lap), (5, 5), 0)
    depth = depth - depth.min()
    if depth.max() > 0:
        depth = depth / depth.max()
    return depth


def depth_scores_for_boxes(
    boxes: Iterable[tuple[int, int, int, int]], depth_map: DepthMap | None
) -> list[float]:
    """Compute average depth per bounding box."""
    if depth_map is None or np is None:
        return [0.5 for _ in boxes]
    scores: list[float] = []
    for box in boxes:
        x, y, w, h = map(int, box)
        if w <= 0 or h <= 0:
            scores.append(0.5)
            continue
        region = depth_map[y : y + h, x : x + w]
        if region.size == 0:
            scores.append(0.5)
        else:
            scores.append(float(region.mean()))
    return scores


def classify_spacing_depth(
    edges: list[dict[str, Any]], depth_lookup: dict[str, float], threshold: float = 0.08
) -> list[dict[str, Any]]:
    """
    Label spacing edges as padding or margin based on relative depth.

    padding: depths within threshold
    margin: depth delta exceeds threshold
    """
    annotated: list[dict[str, Any]] = []
    for edge in edges:
        a = depth_lookup.get(str(edge.get("node_a")), 0.5)
        b = depth_lookup.get(str(edge.get("node_b")), 0.5)
        delta = abs(a - b)
        relation = "padding" if delta <= threshold else "margin"
        enriched = dict(edge)
        enriched["depth_classification"] = relation
        enriched["depth_delta"] = round(float(delta), 4)
        annotated.append(enriched)
    return annotated
