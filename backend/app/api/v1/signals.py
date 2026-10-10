"""
Signals Routes - Urbain Sustainability System
Routes de gestion des signalements urbains
"""

import enum
from typing import Optional, List
from fastapi import UploadFile, File
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin, get_current_sector_user
from app.schemas.signal import (
    SignalCreate, SignalUpdate, SignalResponse, SignalList,
    SignalAnalytics, SignalFilter, SignalStatusUpdate,
    SignalAssignment, SignalFeedback
)
from app.services.signal_service import SignalService
from app.services.file_service import FileService
from app.models.signal import Signal, SignalStatus
from app.core.exceptions import (
    NotFoundError, ValidationError, AuthorizationError,
    DatabaseError, BusinessLogicError
)
from app.utils.helpers import Paginator

logger = structlog.get_logger()
router = APIRouter()


def _serialize_signal(signal):
    data = {}
    for c in signal.__table__.columns:
        val = getattr(signal, c.name)
        data[c.name] = val.value if isinstance(val, enum.Enum) else val
    data["created_by_user"] = _orm_to_dict(signal.created_by_user) if signal.created_by_user else None
    data["processed_by_user"] = _orm_to_dict(signal.processed_by_user) if signal.processed_by_user else None
    data["category"] = _orm_to_dict(signal.category) if signal.category else None
    data["priority"] = _orm_to_dict(signal.priority) if signal.priority else None
    return SignalResponse.model_validate(data).model_dump()

def _serialize_signals(signals):
    return [_serialize_signal(s) for s in signals]

def _orm_to_dict(obj):
    return {c.name: (getattr(obj, c.name).value if isinstance(getattr(obj, c.name), enum.Enum) else getattr(obj, c.name)) for c in obj.__table__.columns}


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create new signal",
    description="Create a new urban issue signal"
)
async def create_signal(
    data: SignalCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        result = await signal_service.create_signal(data, current_user.id)
        return {
            "success": True,
            "message": f"Signal {result.reference_number} created successfully",
            "data": _serialize_signal(result)
        }
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Create signal failed", error=str(e))
        raise ValidationError("Failed to create signal")


@router.get(
    "",
    response_model=dict,
    summary="List signals",
    description="Get paginated list of signals with optional filters"
)
async def list_signals(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    priority_id: Optional[int] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, min_length=2, description="Search title/description"),
    sector_id: Optional[int] = Query(None, description="Filter by sector"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        signal_service = SignalService(db)
        filters = {}
        if status:
            filters["status"] = status
        if category_id:
            filters["category_id"] = category_id
        if priority_id:
            filters["priority_id"] = priority_id
        if sector_id:
            filters["assigned_sector_id"] = sector_id
        if created_by:
            filters["created_by"] = created_by
        if assigned_to:
            filters["assigned_to"] = assigned_to
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if sort_by:
            filters["sort_by"] = sort_by
            filters["sort_order"] = sort_order or "desc"

        if search:
            filters["search"] = search

        signals = await signal_service.get_signals(paginator.skip, paginator.size, filters)

        total_count = await db.execute(select(func.count(Signal.id)))
        total = total_count.scalar() or 0

        return {
            "success": True,
            "message": "Signals retrieved successfully",
            "data": {
                "items": _serialize_signals(signals),
                **paginator.get_metadata(total)
            }
        }
    except Exception as e:
        logger.error("List signals failed", error=str(e))
        raise DatabaseError("Failed to retrieve signals")


@router.get(
    "/search",
    response_model=dict,
    summary="Search signals",
    description="Search signals by title, description, or address"
)
async def search_signals(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        signal_service = SignalService(db)
        signals = await signal_service.search_signals(q, paginator.skip, paginator.size)
        total_result = await db.execute(select(func.count(Signal.id)))
        total = total_result.scalar() or 0
        return {
            "success": True,
            "message": "Signals search completed",
            "data": {
                "items": _serialize_signals(signals),
                **paginator.get_metadata(total)
            }
        }
    except Exception as e:
        logger.error("Search signals failed", error=str(e))
        raise DatabaseError("Failed to search signals")


@router.get(
    "/stats",
    response_model=dict,
    summary="Get signal statistics",
    description="Get aggregate statistics for signals"
)
async def get_signal_stats(
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        stats = await signal_service.get_signal_stats()
        return {
            "success": True,
            "message": "Signal statistics retrieved",
            "data": stats
        }
    except Exception as e:
        logger.error("Get signal stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve signal statistics")


@router.get(
    "/nearby",
    response_model=dict,
    summary="Find nearby signals",
    description="Find signals near specified coordinates within a radius"
)
async def get_nearby_signals(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius: float = Query(5.0, ge=0.1, le=100, description="Search radius in km"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        signal_service = SignalService(db)
        signals = await signal_service.get_nearby_signals(
            latitude, longitude, radius, paginator.skip, paginator.size
        )
        return {
            "success": True,
            "message": f"Nearby signals within {radius}km found",
            "data": {
                "items": _serialize_signals(signals),
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius
            }
        }
    except Exception as e:
        logger.error("Get nearby signals failed", error=str(e))
        raise DatabaseError("Failed to retrieve nearby signals")


@router.get(
    "/{signal_id}",
    response_model=dict,
    summary="Get signal details",
    description="Get detailed information about a specific signal"
)
async def get_signal(
    signal_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        signal = await signal_service.get_signal(signal_id)
        if not signal:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": "Signal retrieved successfully",
            "data": _serialize_signal(signal)
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get signal failed", error=str(e))
        raise NotFoundError(f"Signal with id {signal_id} not found")


@router.put(
    "/{signal_id}",
    response_model=dict,
    summary="Update signal",
    description="Update a signal's details"
)
async def update_signal(
    signal_id: int,
    data: SignalUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        updated = await signal_service.update_signal(signal_id, data, current_user.id)
        if not updated:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": "Signal updated successfully",
            "data": _serialize_signal(updated)
        }
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Update signal failed", error=str(e))
        raise ValidationError("Failed to update signal")


@router.delete(
    "/{signal_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete signal",
    description="Delete a signal"
)
async def delete_signal(
    signal_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        deleted = await signal_service.delete_signal(signal_id, current_user.id)
        if not deleted:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": "Signal deleted successfully"
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Delete signal failed", error=str(e))
        raise NotFoundError(f"Signal with id {signal_id} not found")


@router.post(
    "/{signal_id}/assign",
    response_model=dict,
    summary="Assign signal to sector",
    description="Assign a signal to a user or sector for processing"
)
async def assign_signal(
    signal_id: int,
    data: SignalAssignment,
    current_user = Depends(get_current_sector_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        result = await signal_service.assign_signal(
            signal_id, data.assigned_to_user_id, data.assigned_sector_id, current_user.id
        )
        if not result:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": "Signal assigned successfully",
            "data": _serialize_signal(result)
        }
    except NotFoundError:
        raise
    except BusinessLogicError:
        raise
    except Exception as e:
        logger.error("Assign signal failed", error=str(e))
        raise BusinessLogicError("Failed to assign signal")


@router.post(
    "/{signal_id}/process",
    response_model=dict,
    summary="Mark signal as in progress",
    description="Mark a signal as being processed"
)
async def process_signal(
    signal_id: int,
    data: SignalStatusUpdate,
    current_user = Depends(get_current_sector_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        result = await signal_service.process_signal(
            signal_id, SignalStatus.UNDER_REVIEW,
            user_id=current_user.id, notes=data.notes
        )
        if not result:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": "Signal marked as in progress",
            "data": _serialize_signal(result)
        }
    except NotFoundError:
        raise
    except BusinessLogicError:
        raise
    except Exception as e:
        logger.error("Process signal failed", error=str(e))
        raise BusinessLogicError("Failed to process signal")


@router.post(
    "/{signal_id}/resolve",
    response_model=dict,
    summary="Resolve signal",
    description="Mark a signal as resolved with resolution details"
)
async def resolve_signal(
    signal_id: int,
    data: SignalStatusUpdate,
    current_user = Depends(get_current_sector_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        result = await signal_service.resolve_signal(
            signal_id, current_user.id,
            resolution_description=data.resolution_description,
            resolution_method=data.resolution_method,
            resolution_cost=data.resolution_cost
        )
        if not result:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": "Signal resolved successfully",
            "data": _serialize_signal(result)
        }
    except NotFoundError:
        raise
    except BusinessLogicError:
        raise
    except Exception as e:
        logger.error("Resolve signal failed", error=str(e))
        raise BusinessLogicError("Failed to resolve signal")


@router.post(
    "/{signal_id}/cancel",
    response_model=dict,
    summary="Cancel signal",
    description="Cancel a signal with a reason"
)
async def cancel_signal(
    signal_id: int,
    data: SignalStatusUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        result = await signal_service.cancel_signal(
            signal_id, current_user.id, reason=data.notes
        )
        if not result:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": "Signal cancelled",
            "data": _serialize_signal(result)
        }
    except NotFoundError:
        raise
    except BusinessLogicError:
        raise
    except Exception as e:
        logger.error("Cancel signal failed", error=str(e))
        raise BusinessLogicError("Failed to cancel signal")


@router.post(
    "/{signal_id}/feedback",
    response_model=dict,
    summary="Submit citizen feedback",
    description="Submit satisfaction rating and feedback for a resolved signal"
)
async def submit_feedback(
    signal_id: int,
    data: SignalFeedback,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        result = await signal_service.submit_feedback(
            signal_id=signal_id, user_id=current_user.id,
            satisfaction=data.citizen_satisfaction,
            feedback=data.citizen_feedback
        )
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "data": _serialize_signal(result)
        }
    except NotFoundError:
        raise
    except BusinessLogicError:
        raise
    except AuthorizationError:
        raise
    except Exception as e:
        logger.error("Submit feedback failed", error=str(e))
        raise BusinessLogicError("Failed to submit feedback")


@router.post(
    "/{signal_id}/media",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Upload media to signal",
    description="Upload and attach media files (images) to a signal"
)
async def add_signal_media(
    signal_id: int,
    files: List[UploadFile] = File(..., description="Media files to upload (max 10)"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        if len(files) > 10:
            raise ValidationError("Maximum 10 files allowed per upload")

        file_service = FileService(db)
        signal_service = SignalService(db)
        uploaded_urls = []

        for file in files:
            file_data = await file.read()
            result = await file_service.upload_image(file_data=file_data, filename=file.filename or "image.jpg")
            uploaded_urls.append(result["file_url"])

        result = await signal_service.add_media(
            signal_id=signal_id, media_type="images",
            media_urls=uploaded_urls, user_id=current_user.id
        )
        if not result:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        return {
            "success": True,
            "message": f"{len(uploaded_urls)} file(s) uploaded successfully",
            "data": {"urls": uploaded_urls, "signal": _serialize_signal(result)}
        }
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Upload media failed", error=str(e))
        raise ValidationError("Failed to upload media to signal")


@router.post(
    "/{signal_id}/restore",
    response_model=dict,
    summary="Restore deleted signal",
    description="Restore a soft-deleted signal"
)
async def restore_signal(
    signal_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        result = await signal_service.restore_signal(signal_id, current_user.id)
        return {
            "success": True,
            "message": "Signal restored successfully",
            "data": _serialize_signal(result)
        }
    except (NotFoundError, AuthorizationError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error("Restore signal failed", error=str(e))
        raise BusinessLogicError("Failed to restore signal")


@router.get(
    "/{signal_id}/timeline",
    response_model=dict,
    summary="Get signal timeline",
    description="Get the full status change timeline for a signal"
)
async def get_signal_timeline(
    signal_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        timeline = await signal_service.get_signal_timeline(signal_id)
        return {
            "success": True,
            "message": "Signal timeline retrieved",
            "data": {"items": timeline}
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get timeline failed", error=str(e))
        raise DatabaseError("Failed to get signal timeline")
