"""Caching utilities for extractor pipelines."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Protocol

import redis

logger = logging.getLogger(__name__)

_DEFAULT_TTL = timedelta(hours=6)
_METRICS_LOCK = threading.Lock()
_METRICS: dict[str, Any] = {
    "hits": 0,
    "misses": 0,
    "layer_hits": {},
    "layer_misses": {},
}


class CacheBackend(Protocol):
    def get(self, key: str) -> Any | None: ...

    def set(self, key: str, value: Any, ttl: timedelta | None = None) -> None: ...

    def delete(self, key: str) -> None: ...


class InMemoryBackend:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}

    def get(self, key: str) -> Any | None:
        now = time.time()
        value_ttl = self._store.get(key)
        if not value_ttl:
            return None
        value, expires_at = value_ttl
        if expires_at is not None and expires_at < now:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl: timedelta | None = None) -> None:
        expires_at = None
        if ttl:
            expires_at = time.time() + ttl.total_seconds()
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


class RedisBackend:
    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    def get(self, key: str) -> Any | None:
        try:
            val = self.client.get(key)
            return json.loads(val) if val else None
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis get failed for key %s: %s", key, exc)
            return None

    def set(self, key: str, value: Any, ttl: timedelta | None = None) -> None:
        try:
            payload = json.dumps(value, default=str)
            expire = int((ttl or _DEFAULT_TTL).total_seconds())
            self.client.setex(key, expire, payload)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis set failed for key %s: %s", key, exc)

    def delete(self, key: str) -> None:
        try:
            self.client.delete(key)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis delete failed for key %s: %s", key, exc)


def _record_metric(layer: str, hit: bool) -> None:
    with _METRICS_LOCK:
        counter = "hits" if hit else "misses"
        _METRICS[counter] = int(_METRICS.get(counter, 0)) + 1
        key = "layer_hits" if hit else "layer_misses"
        dct = _METRICS.setdefault(key, {})
        dct[layer] = int(dct.get(layer, 0)) + 1


def get_cache_metrics() -> dict[str, Any]:
    with _METRICS_LOCK:
        return json.loads(json.dumps(_METRICS))


def _default_backend() -> CacheBackend:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        logger.info("REDIS_URL not set; using in-memory cache backend for extractors")
        return InMemoryBackend()
    try:
        client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        client.ping()
        logger.info("Redis cache backend ready for extractors")
        return RedisBackend(client)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis unavailable, falling back to in-memory cache: %s", exc)
        return InMemoryBackend()


_BACKEND: CacheBackend | None = None


def get_extraction_cache() -> ExtractionCache:
    global _BACKEND
    if _BACKEND is None:
        _BACKEND = _default_backend()
    return ExtractionCache(_BACKEND)


def compute_input_hash(
    image_base64: str | None,
    image_url: str | None,
    params: dict[str, Any] | None = None,
) -> str:
    """Stable hash of the input payload (image content or URL + params)."""
    hasher = hashlib.sha256()
    if image_base64:
        payload = image_base64.split(",", 1)[-1]
        try:
            hasher.update(base64.b64decode(payload))
        except Exception:
            hasher.update(payload.encode())
    if image_url:
        hasher.update(image_url.encode())
    if params:
        hasher.update(json.dumps(params, sort_keys=True, default=str).encode())
    return hasher.hexdigest()


@dataclass
class ExtractionCache:
    backend: CacheBackend
    prefix: str = "copythat:extract:"
    ttl: timedelta = _DEFAULT_TTL

    def _key(self, layer: str, input_hash: str, namespace: str | None) -> str:
        ns = namespace or "global"
        return f"{self.prefix}{layer}:{ns}:{input_hash}"

    def get(self, layer: str, input_hash: str, namespace: str | None) -> Any | None:
        key = self._key(layer, input_hash, namespace)
        value = self.backend.get(key)
        _record_metric(layer, hit=value is not None)
        if value is not None:
            logger.info("cache_hit", extra={"cache": {"layer": layer, "namespace": namespace}})
        else:
            logger.info("cache_miss", extra={"cache": {"layer": layer, "namespace": namespace}})
        return value

    def set(
        self,
        layer: str,
        input_hash: str,
        namespace: str | None,
        value: Any,
        ttl: timedelta | None = None,
    ) -> None:
        key = self._key(layer, input_hash, namespace)
        self.backend.set(key, value, ttl or self.ttl)

    def invalidate(self, layer: str, input_hash: str, namespace: str | None) -> None:
        key = self._key(layer, input_hash, namespace)
        self.backend.delete(key)
