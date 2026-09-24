"""Unit tests for mood board image policy router + collage backend."""

from __future__ import annotations

from copy_that.services.mood_board_images.backends import TokenCollageBackend
from copy_that.services.mood_board_images.protocol import Availability, ImageResult
from copy_that.services.mood_board_images.router import PolicyRouter


class _FailBackend:
    id = "fail_cloud"
    kind = "cloud"

    def health(self) -> Availability:
        return Availability(True, estimated_latency_ms=5_000, cost_per_image_usd=0.01, quality=0.9)

    def generate(
        self,
        *,
        prompt: str,
        size: str,
        n: int = 1,
        image_b64: str | None = None,
        strength: float | None = None,
    ) -> list[ImageResult]:
        del image_b64, strength
        raise RuntimeError("boom")


class _OkBackend:
    id = "ok_cloud"
    kind = "cloud"

    def health(self) -> Availability:
        return Availability(True, estimated_latency_ms=8_000, cost_per_image_usd=0.02, quality=0.7)

    def generate(
        self,
        *,
        prompt: str,
        size: str,
        n: int = 1,
        image_b64: str | None = None,
        strength: float | None = None,
    ) -> list[ImageResult]:
        del n, image_b64, strength
        return [ImageResult(url="https://example.com/ok.png", prompt=prompt, provider=self.id)]


def test_router_falls_back_and_records_selection() -> None:
    router = PolicyRouter(backends=[_FailBackend(), _OkBackend(), TokenCollageBackend()])
    result = router.generate_one(
        prompt="palette #112233 material",
        size="512x512",
        policy="balanced",
    )
    assert result is not None
    assert result.provider == "ok_cloud"
    assert result.selection["fallback_from"] == "fail_cloud"
    assert result.selection["policy"] == "balanced"


def test_private_policy_skips_cloud() -> None:
    router = PolicyRouter(backends=[_OkBackend(), TokenCollageBackend()])
    result = router.generate_one(
        prompt="palette #ABCDEF",
        size="256x256",
        policy="private",
    )
    assert result is not None
    assert result.provider == "token_collage"
    assert result.url.startswith("data:image/svg+xml")


def test_circuit_opens_after_failures() -> None:
    router = PolicyRouter(
        backends=[_FailBackend(), TokenCollageBackend()],
        failure_threshold=2,
        cooldown_s=30,
    )
    first = router.generate_one(prompt="#111111", size="256x256", policy="balanced")
    assert first is not None and first.provider == "token_collage"
    # Second failure opens breaker
    router.generate_one(prompt="#222222", size="256x256", policy="balanced")
    health = {row["id"]: row for row in router.health_payload()}
    assert health["fail_cloud"]["available"] is False
    assert health["fail_cloud"]["reason"] == "circuit_open"


def test_reference_image_is_forwarded_with_strength() -> None:
    seen: dict[str, object] = {}

    class _SeeBackend(_OkBackend):
        def generate(
            self,
            *,
            prompt: str,
            size: str,
            n: int = 1,
            image_b64: str | None = None,
            strength: float | None = None,
        ) -> list[ImageResult]:
            seen["image_b64"] = image_b64
            seen["strength"] = strength
            return super().generate(
                prompt=prompt,
                size=size,
                n=n,
                image_b64=image_b64,
                strength=strength,
            )

    router = PolicyRouter(backends=[_SeeBackend()])
    result = router.generate_one(
        prompt="cream control panel",
        size="512x512",
        policy="quality",
        image_b64="abc",
        strength=0.82,
    )
    assert result is not None
    assert seen == {"image_b64": "abc", "strength": 0.82}
    assert result.selection["reference"] == "image"
    assert result.selection["strength"] == 0.82


def test_collage_records_prompt_only_reference() -> None:
    router = PolicyRouter(backends=[TokenCollageBackend()])
    result = router.generate_one(
        prompt="cream control panel #112233",
        size="256x256",
        policy="cheap",
        image_b64="abc",
        strength=0.38,
    )
    assert result is not None
    assert result.selection["reference"] == "prompt_only"
    assert "cream control panel" in result.prompt


def test_collage_always_succeeds() -> None:
    collage = TokenCollageBackend()
    out = collage.generate(prompt="Style tags. Color palette: #ff0000, #00ff00.", size="128x128")
    assert len(out) == 1
    assert "#ff0000" in out[0].url or "ff0000" in out[0].url or out[0].url.startswith("data:")
