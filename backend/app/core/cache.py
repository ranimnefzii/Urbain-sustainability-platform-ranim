import time
import json
import structlog
from typing import Optional, Any, Dict, Callable, Awaitable
from collections import OrderedDict

logger = structlog.get_logger()


class LRUCache:
    def __init__(self, max_size: int = 500, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()

    async def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, expiry = self._cache[key]
        if time.monotonic() > expiry:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expiry = time.monotonic() + (ttl if ttl is not None else self.default_ttl)
        self._cache[key] = (value, expiry)
        self._cache.move_to_end(key)
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    async def delete_pattern(self, pattern: str) -> int:
        prefix = pattern.rstrip("*")
        keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_delete:
            del self._cache[k]
        return len(keys_to_delete)

    async def clear(self) -> None:
        self._cache.clear()

    async def get_or_set(
        self, key: str, factory: Callable[[], Awaitable[Any]],
        ttl: Optional[int] = None
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        await self.set(key, value, ttl)
        return value

    @property
    def size(self) -> int:
        return len(self._cache)

    async def stats(self) -> Dict[str, Any]:
        return {
            "size": self.size,
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
        }


cache = LRUCache()


async def cached(ttl: int = 300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            key_parts = [func.__name__]
            key_parts.extend(str(a) for a in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            return await cache.get_or_set(cache_key, lambda: func(*args, **kwargs), ttl)
        return wrapper
    return decorator
