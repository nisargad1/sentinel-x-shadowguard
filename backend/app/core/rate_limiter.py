import time
import threading
from typing import Dict, List, Tuple, Optional
from app.core.config import settings

class DistributedRateLimiter:
    """
    High-Throughput Sliding-Window Rate Limiter:
      - Limits requests per minute per agent or workspace.
      - Protects upstream MCP servers and downstream tools from runaway AI loops.
      - Supports multi-instance synchronization with Redis or thread-safe in-memory sliding window.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._windows: Dict[str, List[float]] = {}
        self._redis_client = None

        if settings.REDIS_URL:
            try:
                import redis
                client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                client.ping()
                self._redis_client = client
            except Exception:
                pass

    def check_rate_limit(
        self,
        identifier: str,
        limit_per_minute: int = 120
    ) -> Tuple[bool, int, int]:
        """
        Evaluates sliding-window rate limit for the identifier.
        Returns:
            (is_allowed: bool, remaining_requests: int, reset_seconds: int)
        """
        if not settings.RATE_LIMIT_ENABLED:
            return True, limit_per_minute, 60

        now = time.time()
        window_start = now - 60.0

        if self._redis_client:
            try:
                key = f"rate_limit:{identifier}"
                pipe = self._redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(now): now})
                pipe.expire(key, 65)
                _, count, _, _ = pipe.execute()

                if count >= limit_per_minute:
                    return False, 0, 60
                return True, max(0, limit_per_minute - count - 1), 60
            except Exception:
                pass  # Fall back to in-memory on error

        with self._lock:
            timestamps = self._windows.get(identifier, [])
            # Prune timestamps older than 60s
            valid_ts = [ts for ts in timestamps if ts > window_start]

            if len(valid_ts) >= limit_per_minute:
                self._windows[identifier] = valid_ts
                oldest_ts = valid_ts[0] if valid_ts else now
                reset_sec = max(1, int(60 - (now - oldest_ts)))
                return False, 0, reset_sec

            valid_ts.append(now)
            self._windows[identifier] = valid_ts
            remaining = max(0, limit_per_minute - len(valid_ts))
            return True, remaining, 60

    def reset(self, identifier: Optional[str] = None):
        """Resets rate limit state."""
        with self._lock:
            if identifier:
                self._windows.pop(identifier, None)
            else:
                self._windows.clear()

rate_limiter = DistributedRateLimiter()
