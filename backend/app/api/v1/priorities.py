"""
Priority Routes - Urbain Sustainability System
Routes de gestion des priorités de signalements
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.schemas.priority import (
    PriorityCreate, PriorityUpdate, PriorityResponse
)
from app.services.priority_service import PriorityService
from app.core.exceptions import (
    NotFoundError, ValidationError, DatabaseError, BusinessLogicError, ConflictError
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED,
             summary="Create priority", description="Create a new priority level (admin only)")
async def create_priority(
    data: PriorityCreate,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PriorityService(db)
        result = await service.create_priority(obj_in=data)
        return {"success": True, "message": f"Priority '{result.name}' created", "data": PriorityResponse.model_validate(result).model_dump()}
    except ConflictError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Create priority failed", error=str(e))
        raise ValidationError("Failed to create priority")


@router.get("/", response_model=dict, summary="List priorities",
             description="Get all priority levels")
async def list_priorities(
    priority_level: Optional[int] = Query(None, ge=1, le=5, description="Filter by level"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PriorityService(db)
        filters = {}
        if priority_level:
            filters["priority_level"] = priority_level
        priorities = await service.get_priorities(skip=0, limit=100, filters=filters)
        return {"success": True, "message": "Priorities retrieved", "data": [PriorityResponse.model_validate(p).model_dump() for p in priorities]}
    except Exception as e:
        logger.error("List priorities failed", error=str(e))
        raise DatabaseError("Failed to retrieve priorities")


@router.get("/{priority_id}", response_model=dict, summary="Get priority",
             description="Get details of a specific priority")
async def get_priority(
    priority_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PriorityService(db)
        priority = await service.get_priority(priority_id=priority_id)
        return {"success": True, "message": "Priority retrieved", "data": PriorityResponse.model_validate(priority).model_dump()}
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get priority failed", error=str(e))
        raise NotFoundError(f"Priority with id {priority_id} not found")


@router.put("/{priority_id}", response_model=dict, summary="Update priority",
             description="Update a priority's details (admin only)")
async def update_priority(
    priority_id: int,
    data: PriorityUpdate,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PriorityService(db)
        updated = await service.update_priority(priority_id=priority_id, obj_in=data)
        return {"success": True, "message": "Priority updated", "data": PriorityResponse.model_validate(updated).model_dump()}
    except (NotFoundError, ConflictError):
        raise
    except Exception as e:
        logger.error("Update priority failed", error=str(e))
        raise ValidationError("Failed to update priority")


@router.delete("/{priority_id}", response_model=dict, status_code=status.HTTP_200_OK,
               summary="Delete priority", description="Delete a priority (admin only)")
async def delete_priority(
    priority_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PriorityService(db)
        deleted = await service.delete_priority(priority_id=priority_id)
        return {"success": True, "message": "Priority deleted"}
    except (NotFoundError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error("Delete priority failed", error=str(e))
        raise NotFoundError(f"Priority with id {priority_id} not found")


@router.get("/{priority_id}/stats", response_model=dict, summary="Get priority stats",
             description="Get statistics for a specific priority")
async def get_priority_stats(
    priority_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PriorityService(db)
        stats = await service.get_priority_stats(priority_id=priority_id)
        return {"success": True, "message": "Priority stats retrieved", "data": stats}
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get priority stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve priority stats")
