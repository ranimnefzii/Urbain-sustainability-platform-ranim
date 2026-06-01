import functools
import structlog
from typing import Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


def transactional(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        db: AsyncSession = self.db
        try:
            result = await func(self, *args, **kwargs)
            await db.commit()
            return result
        except Exception:
            await db.rollback()
            raise
    return wrapper


def readonly(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        return await func(self, *args, **kwargs)
    return wrapper
