import time
import json
import threading
from typing import Dict, Any, Tuple, Optional
from app.core.config import settings

class DistributedCache:
    """
    Pluggable High-Throughput Cache for SENTINEL-X SmartGuard:
      - Multi-pod distributed caching via Redis when REDIS_URL is configured.
      - Thread-safe, lock-synchronized in-memory cache fallback with TTL expiration and LRU eviction.
      - Tracks real-time hit/miss telemetry for Proof of Value metrics.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._memory_cache: Dict[str, Tuple[float, Any, int]] = {}  # key -> (expiry_ts, result, cost)
        self._max_memory_items = 10000
        self._hits = 0
        self._misses = 0
        self._redis_client = None
        self._backend = "in_memory"

        if settings.REDIS_URL:
            try:
                import redis
                client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                client.ping()
                self._redis_client = client
                self._backend = "redis"
            except Exception:
                self._backend = "in_memory"

    @property
    def backend_type(self) -> str:
        return self._backend

    def get(self, key: str) -> Optional[Tuple[Any, int]]:
        """Retrieves cached result and cost. Returns None if miss or expired."""
        if self._redis_client:
            try:
                raw = self._redis_client.get(key)
                if raw:
                    self._hits += 1
                    data = json.loads(raw)
                    return data.get("result"), data.get("cost", 0)
                self._misses += 1
                return None
            except Exception:
                pass  # Fall back to in-memory on redis connection drop

        now = time.time()
        with self._lock:
            if key in self._memory_cache:
                expiry_ts, result, cost = self._memory_cache[key]
                if now < expiry_ts:
                    self._hits += 1
                    return result, cost
                else:
                    del self._memory_cache[key]
            self._misses += 1
            return None

    def set(self, key: str, result: Any, cost: int, ttl: Optional[int] = None) -> None:
        """Stores result in cache with TTL."""
        ttl_seconds = ttl or settings.CACHE_TTL_SECONDS

        if self._redis_client:
            try:
                payload = json.dumps({"result": result, "cost": cost})
                self._redis_client.setex(key, ttl_seconds, payload)
                return
            except Exception:
                pass

        now = time.time()
        with self._lock:
            # Enforce max capacity eviction if needed
            if len(self._memory_cache) >= self._max_memory_items:
                # Remove oldest expired or first item
                oldest_key = min(self._memory_cache.keys(), key=lambda k: self._memory_cache[k][0])
                del self._memory_cache[oldest_key]
            self._memory_cache[key] = (now + ttl_seconds, result, cost)

    def clear(self) -> None:
        """Clears cache state."""
        if self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass
        with self._lock:
            self._memory_cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> Dict[str, Any]:
        """Returns cache telemetry."""
        total = self._hits + self._misses
        hit_ratio = round((self._hits / total * 100), 1) if total > 0 else 0.0
        return {
            "backend": self._backend,
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio_percent": hit_ratio,
            "active_keys": len(self._memory_cache) if not self._redis_client else "managed_by_redis"
        }

# Global singleton instance
distributed_cache = DistributedCache()
