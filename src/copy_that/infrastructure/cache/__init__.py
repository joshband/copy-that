"""Cache infrastructure package"""

from .extraction_cache import (
    ExtractionCache,
    InMemoryBackend,
    compute_input_hash,
    get_cache_metrics,
    get_extraction_cache,
)
from .redis_cache import (
    RedisCache,
    check_redis_health,
    get_redis,
    is_redis_available,
)

__all__ = [
    "RedisCache",
    "check_redis_health",
    "get_redis",
    "is_redis_available",
    "ExtractionCache",
    "InMemoryBackend",
    "compute_input_hash",
    "get_cache_metrics",
    "get_extraction_cache",
]
