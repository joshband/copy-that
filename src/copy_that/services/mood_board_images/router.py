"""Circuit breaker + policy router for mood board image backends."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from copy_that.services.mood_board_images.protocol import (
    Availability,
    ImageBackend,
    ImageResult,
    RoutingPolicy,
)

logger = logging.getLogger(__name__)


@dataclass
class SelectionMeta:
    provider: str
    policy: RoutingPolicy
    scores: dict[str, float]
    fallback_from: str | None = None


@dataclass
class _BreakerState:
    failures: int = 0
    open_until: float = 0.0


@dataclass
class PolicyRouter:
    """Rank backends and run per-tile fallback chains."""

    backends: list[ImageBackend]
    failure_threshold: int = 2
    cooldown_s: float = 60.0
    _breakers: dict[str, _BreakerState] = field(default_factory=dict)

    def recommended_policy(self) -> RoutingPolicy:
        cloud = any(b.kind == "cloud" and self._effective_health(b).available for b in self.backends)
        local = any(b.kind == "local" and self._effective_health(b).available for b in self.backends)
        if cloud:
            return "balanced"
        if local:
            return "private"
        return "cheap"

    def chain_for(
        self,
        *,
        policy: RoutingPolicy,
        allow_cloud: bool = True,
        focus_type: str = "material",
    ) -> list[ImageBackend]:
        scored: list[tuple[float, ImageBackend, dict[str, float]]] = []
        for backend in self.backends:
            if policy == "private" and backend.kind == "cloud":
                continue
            if not allow_cloud and backend.kind == "cloud":
                continue
            health = self._effective_health(backend)
            if not health.available and backend.kind != "collage":
                continue
            scores = self._score(backend, health, policy=policy, focus_type=focus_type)
            total = scores["total"]
            scored.append((total, backend, scores))
        scored.sort(key=lambda item: item[0], reverse=True)
        # Always ensure collage is last resort if registered
        chain = [b for _, b, _ in scored]
        collage = next((b for b in self.backends if b.id == "token_collage"), None)
        if collage and collage not in chain:
            chain.append(collage)
        elif collage and chain and chain[-1].id != "token_collage":
            chain = [b for b in chain if b.id != "token_collage"] + [collage]
        return chain

    def score_map(
        self,
        *,
        policy: RoutingPolicy,
        allow_cloud: bool = True,
        focus_type: str = "material",
    ) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = {}
        for backend in self.chain_for(policy=policy, allow_cloud=allow_cloud, focus_type=focus_type):
            health = self._effective_health(backend)
            out[backend.id] = self._score(backend, health, policy=policy, focus_type=focus_type)
        return out

    def generate_one(
        self,
        *,
        prompt: str,
        size: str,
        policy: RoutingPolicy,
        allow_cloud: bool = True,
        focus_type: str = "material",
        deadline_monotonic: float | None = None,
        image_b64: str | None = None,
        strength: float | None = None,
    ) -> ImageResult | None:
        chain = self.chain_for(policy=policy, allow_cloud=allow_cloud, focus_type=focus_type)
        scores = self.score_map(policy=policy, allow_cloud=allow_cloud, focus_type=focus_type)
        failed: list[str] = []
        for backend in chain:
            if deadline_monotonic is not None and time.monotonic() > deadline_monotonic:
                logger.info("mood board image deadline hit; stopping chain")
                break
            try:
                results = backend.generate(
                    prompt=prompt,
                    size=size,
                    n=1,
                    image_b64=image_b64,
                    strength=strength,
                )
                if not results:
                    raise RuntimeError("empty result")
                self._record_success(backend.id)
                result = results[0]
                result.provider = backend.id
                prior = dict(result.selection or {})
                reference = prior.get("reference")
                if not reference:
                    reference = "image" if image_b64 else "none"
                result.selection = {
                    "provider": backend.id,
                    "policy": policy,
                    "scores": scores.get(backend.id, {}),
                    "fallback_from": failed[-1] if failed else None,
                    "reference": reference,
                    "strength": strength,
                }
                return result
            except Exception as exc:
                logger.warning("mood board backend %s failed: %s", backend.id, exc)
                self._record_failure(backend.id)
                failed.append(backend.id)
                continue
        return None

    def _effective_health(self, backend: ImageBackend) -> Availability:
        breaker = self._breakers.get(backend.id)
        if breaker and breaker.open_until > time.monotonic():
            return Availability(False, reason="circuit_open")
        return backend.health()

    def _record_success(self, backend_id: str) -> None:
        self._breakers[backend_id] = _BreakerState()

    def _record_failure(self, backend_id: str) -> None:
        state = self._breakers.setdefault(backend_id, _BreakerState())
        state.failures += 1
        if state.failures >= self.failure_threshold:
            state.open_until = time.monotonic() + self.cooldown_s

    def _score(
        self,
        backend: ImageBackend,
        health: Availability,
        *,
        policy: RoutingPolicy,
        focus_type: str,
    ) -> dict[str, float]:
        # Speed: inverse latency (cap)
        latency = max(health.estimated_latency_ms, 1.0)
        speed = max(0.0, min(1.0, 15_000.0 / latency))
        cost = max(0.0, min(1.0, 1.0 - (health.cost_per_image_usd / 0.08)))
        quality = max(0.0, min(1.0, health.quality))
        if focus_type == "typography" and backend.id in {"dalle", "flux_fast"}:
            quality = min(1.0, quality + 0.05)
        availability = 1.0 if health.available or backend.kind == "collage" else 0.0

        weights = {
            "balanced": (0.35, 0.3, 0.2, 0.15),
            "fast": (0.15, 0.55, 0.15, 0.15),
            "cheap": (0.15, 0.2, 0.5, 0.15),
            "private": (0.25, 0.25, 0.1, 0.4),
            "quality": (0.55, 0.15, 0.15, 0.15),
        }[policy]
        w_q, w_s, w_c, w_a = weights
        total = w_q * quality + w_s * speed + w_c * cost + w_a * availability
        if backend.kind == "collage":
            # Prefer real gens unless cheap/private exhausted
            if policy in {"cheap", "private"}:
                total = max(total, 0.4)
            else:
                total *= 0.35
        return {
            "quality": round(quality, 4),
            "speed": round(speed, 4),
            "cost": round(cost, 4),
            "availability": availability,
            "total": round(total, 4),
        }

    def health_payload(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for backend in self.backends:
            h = self._effective_health(backend)
            rows.append(
                {
                    "id": backend.id,
                    "kind": backend.kind,
                    "available": h.available,
                    "reason": h.reason,
                    "estimated_latency_ms": h.estimated_latency_ms,
                    "cost_per_image_usd": h.cost_per_image_usd,
                    "quality": h.quality,
                }
            )
        return rows
