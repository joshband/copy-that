"""Concrete mood board image backends."""

from __future__ import annotations

import base64
import logging
import os
from typing import Any, Literal
from urllib.parse import urlparse

from openai import OpenAI

from copy_that.services.mood_board_images.protocol import Availability, ImageResult

logger = logging.getLogger(__name__)


def _is_local_url(base_url: str) -> bool:
    host = (urlparse(base_url).hostname or "").lower()
    return host in {"127.0.0.1", "localhost", "::1"} or host.endswith(".local")


class OpenaiCompatibleBackend:
    """OpenAI-compatible images.generate (Fal/Replicate proxy or local mflux shim)."""

    def __init__(
        self,
        *,
        backend_id: str,
        kind: Literal["cloud", "local"],
        base_url: str,
        api_key: str,
        model: str,
        size: str = "1024x1024",
        cost_per_image_usd: float = 0.01,
        quality: float = 0.75,
        estimated_latency_ms: float = 8_000.0,
        use_quality_param: bool = False,
    ) -> None:
        self.id = backend_id
        self.kind = kind
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.size = size
        self.cost_per_image_usd = cost_per_image_usd
        self.quality = quality
        self.estimated_latency_ms = estimated_latency_ms
        self.use_quality_param = use_quality_param
        self._client = OpenAI(base_url=self.base_url, api_key=api_key)

    def health(self) -> Availability:
        if not self.base_url:
            return Availability(False, "missing_base_url")
        return Availability(
            True,
            estimated_latency_ms=self.estimated_latency_ms,
            cost_per_image_usd=self.cost_per_image_usd,
            quality=self.quality,
        )

    def generate(self, *, prompt: str, size: str, n: int = 1) -> list[ImageResult]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "n": max(1, n),
            "size": size or self.size,
        }
        if self.use_quality_param:
            kwargs["quality"] = "standard"
        response = self._client.images.generate(**kwargs)
        out: list[ImageResult] = []
        for item in response.data or []:
            url = getattr(item, "url", None)
            b64 = getattr(item, "b64_json", None)
            if not url and b64:
                url = f"data:image/png;base64,{b64}"
            if url:
                out.append(
                    ImageResult(
                        url=url,
                        prompt=prompt,
                        revised_prompt=getattr(item, "revised_prompt", None),
                        provider=self.id,
                    )
                )
        if not out:
            raise RuntimeError(f"{self.id}: empty images.generate response")
        return out


class DalleBackend:
    """OpenAI DALL·E 3."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
    ) -> None:
        self.id = "dalle"
        self.kind: Literal["cloud"] = "cloud"
        self.model = model
        self.size = size
        self._client = OpenAI(api_key=api_key)

    def health(self) -> Availability:
        return Availability(
            True,
            estimated_latency_ms=20_000.0,
            cost_per_image_usd=0.04,
            quality=0.8,
        )

    def generate(self, *, prompt: str, size: str, n: int = 1) -> list[ImageResult]:
        # DALL·E 3 only supports n=1
        response = self._client.images.generate(
            model=self.model,
            prompt=prompt,
            n=1,
            size=size or self.size,
            quality="standard",
        )
        out: list[ImageResult] = []
        for item in response.data or []:
            url = getattr(item, "url", None)
            b64 = getattr(item, "b64_json", None)
            if not url and b64:
                url = f"data:image/png;base64,{b64}"
            if url:
                out.append(
                    ImageResult(
                        url=url,
                        prompt=prompt,
                        revised_prompt=getattr(item, "revised_prompt", None),
                        provider=self.id,
                    )
                )
        if not out:
            raise RuntimeError("dalle: empty images.generate response")
        return out


class TokenCollageBackend:
    """Deterministic SVG collage from theme hexes — no network."""

    def __init__(self) -> None:
        self.id = "token_collage"
        self.kind: Literal["collage"] = "collage"

    def health(self) -> Availability:
        return Availability(
            True,
            reason="always",
            estimated_latency_ms=5.0,
            cost_per_image_usd=0.0,
            quality=0.45,
        )

    def generate(self, *, prompt: str, size: str, n: int = 1) -> list[ImageResult]:
        hexes = _hexes_from_prompt(prompt)
        w, h = _parse_size(size)
        svg = _build_collage_svg(hexes, w, h, prompt)
        encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        url = f"data:image/svg+xml;base64,{encoded}"
        return [
            ImageResult(url=url, prompt=prompt, provider=self.id)
            for _ in range(max(1, n))
        ]


def _parse_size(size: str) -> tuple[int, int]:
    try:
        parts = size.lower().split("x")
        return max(64, int(parts[0])), max(64, int(parts[1]))
    except (ValueError, IndexError, AttributeError):
        return 1024, 1024


def _hexes_from_prompt(prompt: str) -> list[str]:
    import re

    found = re.findall(r"#[0-9A-Fa-f]{6}", prompt)
    if found:
        return found[:6]
    # Stable fallback palette from prompt hash
    seed = abs(hash(prompt)) % (16**6)
    return [f"#{(seed + i * 0x314159) % (16**6):06x}" for i in range(4)]


def _build_collage_svg(hexes: list[str], w: int, h: int, prompt: str) -> str:
    colors = hexes or ["#1e293b", "#64748b", "#94a3b8", "#e2e8f0"]
    n = len(colors)
    cols = 2 if n > 1 else 1
    rows = (n + cols - 1) // cols
    cell_w = w / cols
    cell_h = h / rows
    rects = []
    for i, color in enumerate(colors):
        c = i % cols
        r = i // cols
        rects.append(
            f'<rect x="{c * cell_w:.1f}" y="{r * cell_h:.1f}" '
            f'width="{cell_w:.1f}" height="{cell_h:.1f}" fill="{color}"/>'
        )
    title = (prompt[:80] + "…") if len(prompt) > 80 else prompt
    safe_title = (
        title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="100%" height="100%" fill="#0f172a"/>'
        f"{''.join(rects)}"
        f'<text x="24" y="{h - 24}" fill="#f8fafc" font-family="ui-monospace,monospace" '
        f'font-size="18">{safe_title}</text>'
        f"</svg>"
    )


def build_compatible_backend_from_env(
    *,
    backend_id: str,
    kind: Literal["cloud", "local"] | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> OpenaiCompatibleBackend | None:
    """Factory for env-configured OpenAI-compatible backends."""
    url = (base_url or "").strip().rstrip("/")
    if not url:
        return None
    resolved_kind: Literal["cloud", "local"] = kind or (
        "local" if _is_local_url(url) else "cloud"
    )
    key = (
        api_key
        or os.getenv("MOOD_BOARD_IMAGE_API_KEY")
        or os.getenv("MOOD_BOARD_FLUX_API_KEY")
        or os.getenv("FAL_KEY")
        or os.getenv("REPLICATE_API_TOKEN")
        or "local"
    )
    resolved_model = model or os.getenv("MOOD_BOARD_IMAGE_MODEL") or "flux-schnell"
    size = os.getenv("MOOD_BOARD_IMAGE_SIZE", "1024x1024")
    if resolved_kind == "local":
        return OpenaiCompatibleBackend(
            backend_id=backend_id,
            kind="local",
            base_url=url,
            api_key=key,
            model=resolved_model,
            size=size,
            cost_per_image_usd=0.0,
            quality=0.7,
            estimated_latency_ms=300_000.0,
            use_quality_param=False,
        )
    return OpenaiCompatibleBackend(
        backend_id=backend_id,
        kind="cloud",
        base_url=url,
        api_key=key,
        model=resolved_model or os.getenv("MOOD_BOARD_FLUX_MODEL") or "flux-schnell",
        size=size,
        cost_per_image_usd=0.01,
        quality=0.78,
        estimated_latency_ms=8_000.0,
        use_quality_param=False,
    )
