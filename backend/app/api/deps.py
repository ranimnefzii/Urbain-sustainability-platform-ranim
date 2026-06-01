"""
API Dependencies - Urbain Sustainability System
Dépendances partagées pour les routes API
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise AuthenticationError("Authentication required")
    
    payload = verify_token(credentials.credentials)
    user_id = int(payload.get("sub"))
    
    user_repo = UserRepository(db, User)
    user = await user_repo.get(id=user_id)
    
    if not user:
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    
    return user


async def get_current_admin(current_user = Depends(get_current_user)):
    """Require admin role"""
    if not current_user.is_admin:
        raise AuthorizationError("Admin access required")
    return current_user


async def get_current_sector_user(current_user = Depends(get_current_user)):
    """Require sector user role"""
    if not current_user.is_sector_user and not current_user.is_admin:
        raise AuthorizationError("Sector access required")
    return current_user


async def get_current_citizen(current_user = Depends(get_current_user)):
    """Require citizen role"""
    if not current_user.is_citizen:
        raise AuthorizationError("Citizen access required")
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
):
    """Get current user if token provided, otherwise None"""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        user_repo = UserRepository(db, User)
        return await user_repo.get(id=user_id)
    except Exception:
        return None


class RoleChecker:
    """Check if user has required role"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user = Depends(get_current_user)):
        if current_user.role.value not in self.allowed_roles:
            raise AuthorizationError(
                f"Role '{current_user.role.value}' not allowed. Required: {self.allowed_roles}"
            )
        return current_user
