"""
Users Routes - Urbain Sustainability System
Routes de gestion des utilisateurs (admin)
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.schemas.user import UserResponse, UserUpdate, UserStats
from app.schemas.signal import SignalResponse
from app.services.user_service import UserService
from app.services.signal_service import SignalService
from app.core.exceptions import (
    NotFoundError, ValidationError, AuthorizationError,
    BusinessLogicError, DatabaseError
)
from app.utils.helpers import Paginator

logger = structlog.get_logger()
router = APIRouter()


def _serialize_user(user) -> Dict[str, Any]:
    cols = ["id", "email", "username", "first_name", "last_name", "phone_number",
            "profile_picture_url", "is_email_verified", "created_at", "updated_at"]
    result = {}
    for c in cols:
        val = getattr(user, c, None)
        if hasattr(val, 'value'):
            val = val.value
        result[c] = val
    result["role"] = user.role.value if hasattr(user.role, 'value') else user.role
    result["status"] = user.status.value if hasattr(user.status, 'value') else user.status
    return result


def _serialize_signal_basic(signal) -> Dict[str, Any]:
    cols = ["id", "title", "description", "reference_number", "status", "source",
            "latitude", "longitude", "address", "city", "created_at", "updated_at"]
    result = {}
    for c in cols:
        val = getattr(signal, c, None)
        if hasattr(val, 'value'):
            val = val.value
        result[c] = val
    return result


@router.get(
    "",
    response_model=dict,
    summary="List users",
    description="Get paginated list of all users (admin only)"
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        user_service = UserService(db)
        filters = {}
        if role:
            filters["role"] = role
        if status:
            filters["status"] = status
        users = await user_service.get_users(skip=paginator.skip, limit=paginator.size, filters=filters)
        total = len(users)
        return {
            "success": True,
            "message": "Users retrieved successfully",
            "data": {
                "items": [_serialize_user(u) for u in users],
                **paginator.get_metadata(total)
            }
        }
    except Exception as e:
        logger.error("List users failed", error=str(e))
        raise DatabaseError("Failed to retrieve users")


@router.get(
    "/search",
    response_model=dict,
    summary="Search users",
    description="Search users by name, email, or username (admin only)"
)
async def search_users(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        user_service = UserService(db)
        users = await user_service.search_users(search_term=q, skip=paginator.skip, limit=paginator.size)
        total = len(users)
        return {
            "success": True,
            "message": "Users search completed",
            "data": {
                "items": users,
                **paginator.get_metadata(total)
            }
        }
    except Exception as e:
        logger.error("Search users failed", error=str(e))
        raise DatabaseError("Failed to search users")


@router.get(
    "/{user_id}",
    response_model=dict,
    summary="Get user by ID",
    description="Get a specific user's details"
)
async def get_user(
    user_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        user = await user_service.get_user(user_id=user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        return {
            "success": True,
            "message": "User retrieved successfully",
            "data": _serialize_user(user)
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get user failed", error=str(e))
        raise NotFoundError(f"User with id {user_id} not found")


@router.put(
    "/{user_id}",
    response_model=dict,
    summary="Update user",
    description="Update a user's details (admin only)"
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        updated = await user_service.update_user(user_id=user_id, obj_in=data, current_user_id=current_user.id)
        if not updated:
            raise NotFoundError(f"User with id {user_id} not found")
        return {
            "success": True,
            "message": "User updated successfully",
            "data": _serialize_user(updated)
        }
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Update user failed", error=str(e))
        raise ValidationError("Failed to update user")


@router.delete(
    "/{user_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Delete a user (admin only)"
)
async def delete_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        deleted = await user_service.delete_user(user_id=user_id, current_user_id=current_user.id)
        if not deleted:
            raise NotFoundError(f"User with id {user_id} not found")
        return {
            "success": True,
            "message": "User deleted successfully"
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Delete user failed", error=str(e))
        raise NotFoundError(f"User with id {user_id} not found")


@router.get(
    "/{user_id}/signals",
    response_model=dict,
    summary="Get user's signals",
    description="Get all signals created by a specific user"
)
async def get_user_signals(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        signal_service = SignalService(db)
        signals = await signal_service.get_user_signals(user_id=user_id, skip=paginator.skip, limit=paginator.size)
        total = len(signals)
        return {
            "success": True,
            "message": "User signals retrieved successfully",
            "data": {
                "items": [_serialize_signal_basic(s) for s in signals],
                **paginator.get_metadata(total)
            }
        }
    except Exception as e:
        logger.error("Get user signals failed", error=str(e))
        raise DatabaseError("Failed to retrieve user signals")


@router.get(
    "/{user_id}/stats",
    response_model=dict,
    summary="Get user statistics",
    description="Get statistics for a specific user"
)
async def get_user_stats(
    user_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        stats = await user_service.get_user_stats(user_id=user_id)
        if not stats:
            raise NotFoundError(f"User with id {user_id} not found")
        return {
            "success": True,
            "message": "User stats retrieved successfully",
            "data": stats
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get user stats failed", error=str(e))
        raise NotFoundError(f"User with id {user_id} not found")


@router.put(
    "/{user_id}/activate",
    response_model=dict,
    summary="Activate user",
    description="Activate a user account (admin only)"
)
async def activate_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        result = await user_service.activate_user(user_id=user_id)
        if not result:
            raise NotFoundError(f"User with id {user_id} not found")
        return {
            "success": True,
            "message": "User activated successfully"
        }
    except NotFoundError:
        raise
    except BusinessLogicError:
        raise
    except Exception as e:
        logger.error("Activate user failed", error=str(e))
        raise DatabaseError("Failed to activate user")


@router.put(
    "/{user_id}/deactivate",
    response_model=dict,
    summary="Deactivate user",
    description="Deactivate a user account (admin only)"
)
async def deactivate_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        result = await user_service.deactivate_user(user_id=user_id)
        if not result:
            raise NotFoundError(f"User with id {user_id} not found")
        return {
            "success": True,
            "message": "User deactivated successfully"
        }
    except NotFoundError:
        raise
    except BusinessLogicError:
        raise
    except Exception as e:
        logger.error("Deactivate user failed", error=str(e))
        raise DatabaseError("Failed to deactivate user")
