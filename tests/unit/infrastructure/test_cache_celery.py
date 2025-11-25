import importlib

import pytest

from copy_that.infrastructure.cache import redis_cache

celery_app_module = importlib.import_module("copy_that.infrastructure.celery.app")


class DummyAsyncRedis:
    def __init__(self):
        self.storage = {}

    async def ping(self):
        return True

    async def get(self, key):
        return self.storage.get(key)

    async def setex(self, key, ttl, value):
        self.storage[key] = value

    async def delete(self, *keys):
        for key in keys:
            self.storage.pop(key, None)

    async def keys(self, pattern):
        return [k for k in self.storage if k.startswith(pattern)]

    async def info(self, section):
        return {"redis_version": "7.0", "connected_clients": 1}


@pytest.mark.asyncio
async def test_get_or_set_caching(monkeypatch):
    fake_redis = DummyAsyncRedis()
    cache = redis_cache.RedisCache(fake_redis)

    async def factory():
        return {"value": 42}

    # populate cache via get_or_set
    result = await cache.get_or_set("tokens", "primary", factory)
    assert result == {"value": 42}

    # subsequent call should retrieve cached value without rerunning factory
    result2 = await cache.get_or_set("tokens", "primary", lambda: factory())
    assert result2 == {"value": 42}

    # ensure delete works
    await cache.delete("tokens", "primary")
    assert await cache.get("tokens", "primary") is None

    await cache.set("tokens", "primary", {"value": 7})
    assert await cache.get("tokens", "primary") == {"value": 7}


@pytest.mark.asyncio
async def test_check_redis_health_not_configured(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    status = await redis_cache.check_redis_health()
    assert status["status"] == "not_configured"


def test_robust_redis_connection_success(monkeypatch):
    class FakeRedisClient:
        def __init__(self):
            self.ping_called = False

        def ping(self):
            self.ping_called = True

    fake_instance = FakeRedisClient()

    def fake_redis(**kwargs):
        return fake_instance

    monkeypatch.setattr(celery_app_module.redis, "Redis", fake_redis)
    assert celery_app_module.robust_redis_connection(max_retries=1) is fake_instance


def test_robust_redis_connection_failure(monkeypatch):
    class BadClient:
        def ping(self):
            raise RuntimeError("fail")

    def bad_redis(**kwargs):
        return BadClient()

    monkeypatch.setattr(celery_app_module.redis, "Redis", bad_redis)
    assert celery_app_module.robust_redis_connection(max_retries=1) is None


def test_test_redis_connection_false(monkeypatch):
    monkeypatch.setattr(celery_app_module, "robust_redis_connection", lambda: None)
    assert celery_app_module.test_redis_connection() is False


def test_test_redis_connection_true(monkeypatch):
    class Dummy:
        def ping(self):
            pass

    monkeypatch.setattr(celery_app_module, "robust_redis_connection", lambda: Dummy())
    assert celery_app_module.test_redis_connection() is True
