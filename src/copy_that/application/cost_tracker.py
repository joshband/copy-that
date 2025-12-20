"""Cost tracking and quota enforcement for AI inference."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

import redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class CostBackend(Protocol):
    def get(self, key: str) -> Any | None: ...

    def set(self, key: str, value: Any) -> None: ...


class InMemoryCostBackend:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        return self.store.get(key)

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value


class RedisCostBackend:
    def __init__(self, url: str) -> None:
        self.client = redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )

    def get(self, key: str) -> Any | None:
        try:
            val = self.client.get(key)
            return json.loads(val) if val else None
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to read cost key %s: %s", key, exc)
            return None

    def set(self, key: str, value: Any) -> None:
        try:
            self.client.set(key, json.dumps(value))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to write cost key %s: %s", key, exc)


def _backend() -> CostBackend:
    url = os.getenv("REDIS_URL")
    if not url:
        logger.info("REDIS_URL not set; using in-memory cost backend")
        return InMemoryCostBackend()
    try:
        backend = RedisCostBackend(url)
        backend.set("cost:ping", {"ts": time.time()})
        return backend
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis unavailable for cost tracking, using memory backend: %s", exc)
        return InMemoryCostBackend()


def _today() -> str:
    return datetime.now(UTC).date().isoformat()


@dataclass
class CostState:
    total: float
    window: str
    soft_limit: float
    hard_limit: float
    blocked: bool
    warned: bool
    persisted: bool


class CostTracker:
    def __init__(self, backend: CostBackend | None = None) -> None:
        self.backend = backend or _backend()
        self.soft_limit = float(os.getenv("COST_SOFT_LIMIT_USD", "5.0"))
        self.hard_limit = float(os.getenv("COST_HARD_LIMIT_USD", "10.0"))

    def _soft_limit_effective(self) -> float:
        """Clamp soft limit when a lower hard limit is configured."""
        if self.hard_limit > 0:
            return min(self.soft_limit, self.hard_limit * 0.6)
        return self.soft_limit

    def _key(self, project_id: int) -> str:
        return f"cost:project:{project_id}"

    def _load(self, project_id: int) -> dict[str, Any]:
        record = self.backend.get(self._key(project_id)) or {}
        if record.get("window") != _today():
            return {"total": 0.0, "window": _today()}
        return record

    def record(self, project_id: int, amount: float) -> CostState:
        state = self._load(project_id)
        state["total"] = float(state.get("total", 0.0)) + amount
        state["window"] = _today()
        self.backend.set(self._key(project_id), state)

        blocked = state["total"] >= self.hard_limit > 0
        soft_limit_effective = self._soft_limit_effective()
        warned = state["total"] >= soft_limit_effective > 0 and not blocked

        return CostState(
            total=state["total"],
            window=state["window"],
            soft_limit=soft_limit_effective,
            hard_limit=self.hard_limit,
            blocked=blocked,
            warned=warned,
            persisted=False,
        )

    def get(self, project_id: int) -> CostState:
        state = self._load(project_id)
        soft_limit_effective = self._soft_limit_effective()
        return CostState(
            total=float(state.get("total", 0.0)),
            window=state.get("window", _today()),
            soft_limit=soft_limit_effective,
            hard_limit=self.hard_limit,
            blocked=False,
            warned=False,
            persisted=False,
        )

    async def persist(
        self, session: AsyncSession, project_id: int, state: CostState | None = None
    ) -> None:
        """Persist cost totals into the database."""
        from copy_that.infrastructure.persistence import models

        if state is None:
            state = self.get(project_id)

        result = await session.execute(
            select(models.ProjectCost).where(
                models.ProjectCost.project_id == project_id,
                models.ProjectCost.window == state.window,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.total_usd = state.total
            existing.soft_limit_usd = state.soft_limit
            existing.hard_limit_usd = state.hard_limit
        else:
            record = models.ProjectCost(
                project_id=project_id,
                window=state.window,
                total_usd=state.total,
                soft_limit_usd=state.soft_limit,
                hard_limit_usd=state.hard_limit,
            )
            session.add(record)
        await session.commit()


cost_tracker = CostTracker()
