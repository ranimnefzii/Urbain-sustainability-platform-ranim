import time
import structlog
from typing import Dict, Tuple, Optional
from collections import defaultdict

from app.core.config import settings
from app.core.exceptions import RateLimitError

logger = structlog.get_logger()


class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
        self.last_refill = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class InMemoryRateLimiter:
    def __init__(self):
        self.buckets: Dict[str, Tuple[TokenBucket, float]] = {}
        self._cleanup_interval = 300.0
        self._last_cleanup = time.monotonic()

    def _cleanup(self):
        now = time.monotonic()
        if now - self._last_cleanup > self._cleanup_interval:
            stale_keys = [k for k, (_, ts) in self.buckets.items() if now - ts > 3600]
            for k in stale_keys:
                del self.buckets[k]
            self._last_cleanup = now

    def check_rate_limit(
        self,
        key: str,
        max_requests: int = 0,
        window_seconds: int = 0,
    ) -> bool:
        max_req = max_requests or settings.RATE_LIMIT_MAX_REQUESTS
        window = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        fill_rate = max_req / window if window > 0 else float('inf')

        self._cleanup()
        if key not in self.buckets:
            self.buckets[key] = (TokenBucket(max_req, fill_rate), time.monotonic())
        bucket, _ = self.buckets[key]
        self.buckets[key] = (bucket, time.monotonic())
        return bucket.consume(1)


rate_limiter = InMemoryRateLimiter()


async def check_rate_limit(
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    action: str = "default",
    max_requests: int = 0,
    window_seconds: int = 0,
) -> None:
    key_parts = []
    if user_id:
        key_parts.append(f"user:{user_id}")
    if ip_address:
        key_parts.append(f"ip:{ip_address}")
    key_parts.append(action)
    key = ":".join(key_parts)

    if not rate_limiter.check_rate_limit(key, max_requests, window_seconds):
        logger.warning("Rate limit exceeded", key=key, user_id=user_id)
        raise RateLimitError(
            f"Rate limit exceeded. Try again later.",
            details={"retry_after_seconds": 60}
        )


async def check_auth_rate_limit(ip_address: str) -> None:
    await check_rate_limit(
        ip_address=ip_address,
        action="auth",
        max_requests=getattr(settings, "RATE_LIMIT_AUTH_MAX", 5),
        window_seconds=60,
    )


async def check_api_rate_limit(user_id: int, ip_address: str) -> None:
    await check_rate_limit(
        user_id=user_id,
        ip_address=ip_address,
        action="api",
        max_requests=getattr(settings, "RATE_LIMIT_API_MAX", 200),
        window_seconds=60,
    )
