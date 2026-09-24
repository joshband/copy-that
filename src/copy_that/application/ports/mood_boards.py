from __future__ import annotations

from typing import Any, Protocol


class MoodBoardGenerator(Protocol):
    async def generate(
        self,
        *,
        colors: list[Any],
        prompt: str | None = None,
        num_variants: int = 2,
        include_images: bool = True,
        num_images_per_variant: int = 4,
        focus_type: str = "material",
        image_slots: list[Any] | None = None,
    ) -> dict: ...
