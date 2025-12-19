import time
from datetime import timedelta

from copy_that.infrastructure.cache.extraction_cache import (
    ExtractionCache,
    InMemoryBackend,
    compute_input_hash,
)


def test_compute_input_hash_changes_with_params():
    base = compute_input_hash("data:image/png;base64,aaa", None, {"a": 1})
    diff = compute_input_hash("data:image/png;base64,aaa", None, {"a": 2})
    assert base != diff


def test_extraction_cache_is_namespaced():
    backend = InMemoryBackend()
    cache = ExtractionCache(backend, prefix="test:", ttl=timedelta(hours=6))

    cache.set("color.full", "hash1", "project:1", {"v": 1})
    cache.set("color.full", "hash1", "project:2", {"v": 2})

    assert cache.get("color.full", "hash1", "project:1") == {"v": 1}
    assert cache.get("color.full", "hash1", "project:2") == {"v": 2}


def test_extraction_cache_respects_ttl():
    backend = InMemoryBackend()
    cache = ExtractionCache(backend, prefix="test:", ttl=timedelta(seconds=0.1))
    cache.set("color.full", "hash1", "project:1", {"v": 1})
    assert cache.get("color.full", "hash1", "project:1") == {"v": 1}
    time.sleep(0.2)
    assert cache.get("color.full", "hash1", "project:1") is None
