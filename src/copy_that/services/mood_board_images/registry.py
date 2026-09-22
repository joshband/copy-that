"""Build mood board image backend registry from environment."""

from __future__ import annotations

import os
from typing import Any

from copy_that.services.mood_board_images.backends import (
    DalleBackend,
    TokenCollageBackend,
    build_compatible_backend_from_env,
    _is_local_url,
)
from copy_that.services.mood_board_images.protocol import ImageBackend
from copy_that.services.mood_board_images.router import PolicyRouter


def build_image_backends(
    *,
    image_base_url: str | None = None,
    image_api_key: str | None = None,
    image_model: str | None = None,
    openai_api_key: str | None = None,
) -> list[ImageBackend]:
    """Assemble backends: flux_fast / local_mflux / dalle / token_collage."""
    backends: list[ImageBackend] = []

    flux_url = (os.getenv("MOOD_BOARD_FLUX_BASE_URL") or "").strip()
    image_url = (image_base_url or os.getenv("MOOD_BOARD_IMAGE_BASE_URL") or "").strip()

    if flux_url:
        flux = build_compatible_backend_from_env(
            backend_id="flux_fast",
            kind="cloud",
            base_url=flux_url,
            api_key=image_api_key
            or os.getenv("MOOD_BOARD_FLUX_API_KEY")
            or os.getenv("FAL_KEY")
            or os.getenv("REPLICATE_API_TOKEN"),
            model=image_model or os.getenv("MOOD_BOARD_FLUX_MODEL") or "flux-schnell",
        )
        if flux:
            backends.append(flux)

    if image_url:
        if _is_local_url(image_url):
            local = build_compatible_backend_from_env(
                backend_id="local_mflux",
                kind="local",
                base_url=image_url,
                api_key=image_api_key,
                model=image_model or os.getenv("MOOD_BOARD_IMAGE_MODEL") or "schnell",
            )
            if local:
                backends.append(local)
        elif not flux_url:
            # Non-local IMAGE_BASE_URL without dedicated FLUX URL → treat as flux_fast
            cloud = build_compatible_backend_from_env(
                backend_id="flux_fast",
                kind="cloud",
                base_url=image_url,
                api_key=image_api_key,
                model=image_model
                or os.getenv("MOOD_BOARD_FLUX_MODEL")
                or os.getenv("MOOD_BOARD_IMAGE_MODEL")
                or "flux-schnell",
            )
            if cloud:
                backends.append(cloud)

    # Fal key without explicit URL: document-required FLUX_BASE_URL; no silent guess.

    openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if openai_key:
        backends.append(
            DalleBackend(
                api_key=openai_key,
                size=os.getenv("MOOD_BOARD_IMAGE_SIZE", "1024x1024"),
            )
        )

    backends.append(TokenCollageBackend())
    return backends


def build_router(**kwargs: Any) -> PolicyRouter:
    return PolicyRouter(backends=build_image_backends(**kwargs))


def health_snapshot(**kwargs: Any) -> dict[str, Any]:
    router = build_router(**kwargs)
    return {
        "backends": router.health_payload(),
        "recommended_policy": router.recommended_policy(),
        "default_policy": os.getenv("MOOD_BOARD_ROUTING_POLICY", "balanced"),
    }
