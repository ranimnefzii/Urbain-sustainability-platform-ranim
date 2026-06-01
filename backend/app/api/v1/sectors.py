from typing import Optional, Any, Dict, List
from datetime import datetime
import enum
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.schemas.sector import (
    SectorCreate, SectorUpdate, SectorResponse,
    SectorStats, SectorPerformance, SectorWorkload
)
from app.services.sector_service import SectorService
from app.core.exceptions import (
    NotFoundError, ValidationError, DatabaseError, ConflictError, BusinessLogicError
)
from app.utils.helpers import Paginator
from app.models.sector import Sector, SectorStatus

logger = structlog.get_logger()
router = APIRouter()


def _serialize_sector(sector: Sector) -> Dict[str, Any]:
    data = {}
    for c in sector.__table__.columns:
        val = getattr(sector, c.name)
        if isinstance(val, enum.Enum):
            data[c.name] = val.value
        elif isinstance(val, datetime):
            data[c.name] = val.isoformat() if val else None
        else:
            data[c.name] = val
    return SectorResponse(**data).model_dump()


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create sector",
    description="Create a new municipal sector (admin only)"
)
async def create_sector(
    data: SectorCreate,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        sector_service = SectorService(db)
        result = await sector_service.create_sector(obj_in=data)
        return {
            "success": True,
            "message": f"Sector '{result.name}' created successfully",
            "data": _serialize_sector(result)
        }
    except (ValidationError, ConflictError):
        raise
    except Exception as e:
        logger.error("Create sector failed", error=str(e))
        raise ValidationError("Failed to create sector")


@router.get(
    "/",
    response_model=dict,
    summary="List sectors",
    description="Get all sectors with optional filtering"
)
async def list_sectors(
    sector_type: Optional[str] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        sector_service = SectorService(db)
        filters = {}
        if sector_type:
            filters["sector_type"] = sector_type
        if status:
            filters["status"] = status
        sectors = await sector_service.get_sectors(skip=0, limit=100, filters=filters)
        return {
            "success": True,
            "message": "Sectors retrieved successfully",
            "data": [_serialize_sector(s) for s in sectors]
        }
    except Exception as e:
        logger.error("List sectors failed", error=str(e))
        raise DatabaseError("Failed to retrieve sectors")


@router.get(
    "/{sector_id}",
    response_model=dict,
    summary="Get sector details",
    description="Get detailed information about a specific sector"
)
async def get_sector(
    sector_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        sector_service = SectorService(db)
        sector = await sector_service.get_sector(sector_id=sector_id)
        if not sector:
            raise NotFoundError(f"Sector with id {sector_id} not found")
        return {
            "success": True,
            "message": "Sector retrieved successfully",
            "data": _serialize_sector(sector)
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get sector failed", error=str(e))
        raise NotFoundError(f"Sector with id {sector_id} not found")


@router.put(
    "/{sector_id}",
    response_model=dict,
    summary="Update sector",
    description="Update a sector's details (admin only)"
)
async def update_sector(
    sector_id: int,
    data: SectorUpdate,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        sector_service = SectorService(db)
        updated = await sector_service.update_sector(sector_id=sector_id, obj_in=data)
        if not updated:
            raise NotFoundError(f"Sector with id {sector_id} not found")
        return {
            "success": True,
            "message": "Sector updated successfully",
            "data": _serialize_sector(updated)
        }
    except (NotFoundError, ConflictError):
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Update sector failed", error=str(e))
        raise ValidationError("Failed to update sector")


@router.delete(
    "/{sector_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete sector",
    description="Delete a sector (admin only)"
)
async def delete_sector(
    sector_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        sector_service = SectorService(db)
        deleted = await sector_service.delete_sector(sector_id=sector_id)
        if not deleted:
            raise NotFoundError(f"Sector with id {sector_id} not found")
        return {
            "success": True,
            "message": "Sector deleted successfully"
        }
    except (NotFoundError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error("Delete sector failed", error=str(e))
        raise NotFoundError(f"Sector with id {sector_id} not found")


@router.get(
    "/{sector_id}/stats",
    response_model=dict,
    summary="Get sector statistics",
    description="Get comprehensive statistics for a specific sector"
)
async def get_sector_stats(
    sector_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        sector_service = SectorService(db)
        stats = await sector_service.get_sector_stats(sector_id=sector_id)
        return {
            "success": True,
            "message": "Sector statistics retrieved",
            "data": stats
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get sector stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve sector statistics")
