"""
Global Dependencies - Urbain Sustainability System
Dépendances globales et injections FastAPI
"""

from typing import Optional, List
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import RateLimitError


# Simple in-memory rate limiter (replace with Redis in production)
_rate_limit_store: dict = {}


async def rate_limiter(request: Request):
    """Rate limiting dependency"""
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    key = f"{client_ip}:{path}"
    
    from time import time
    current = time()
    window = 60
    
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    
    _rate_limit_store[key] = [
        t for t in _rate_limit_store[key] 
        if current - t < window
    ]
    
    if len(_rate_limit_store[key]) >= settings.RATE_LIMIT_PER_MINUTE:
        raise RateLimitError("Rate limit exceeded. Please try again later.")
    
    _rate_limit_store[key].append(current)


async def pagination_deps(
    page: int = 1,
    size: int = 20,
    sort: str = "created_at",
    order: str = "desc"
):
    """Pagination query parameters"""
    from app.utils.helpers import Paginator
    paginator = Paginator(page=page, size=size)
    return {
        "paginator": paginator,
        "sort": sort,
        "order": order
    }


async def get_current_db(request: Request) -> AsyncSession:
    """Get database session from request state"""
    return request.state.db


async def get_settings():
    """Get application settings"""
    return settings
