from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.services.audit_service import AuditService
from app.core.exceptions import DatabaseError

router = APIRouter()


@router.get("", response_model=dict, summary="List audit logs",
             description="Get paginated audit log entries with optional filters")
async def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=200, description="Page size"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_date: Optional[str] = Query(None, description="Start date (ISO)"),
    end_date: Optional[str] = Query(None, description="End date (ISO)"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AuditService(db)
        skip = (page - 1) * size
        logs = await service.get_logs(
            skip=skip, limit=size,
            entity_type=entity_type, entity_id=entity_id,
            action=action, user_id=user_id,
            severity=severity, start_date=start_date, end_date=end_date,
        )
        total = await service.count_logs(
            entity_type=entity_type, entity_id=entity_id,
            action=action, user_id=user_id,
        )
        return {
            "success": True,
            "message": "Audit logs retrieved",
            "data": {
                "items": [
                    {
                        "id": log.id,
                        "action": log.action,
                        "entity_type": log.entity_type,
                        "entity_id": log.entity_id,
                        "user_id": log.user_id,
                        "old_values": log.old_values,
                        "new_values": log.new_values,
                        "metadata": log.log_metadata,
                        "severity": log.severity,
                        "ip_address": log.ip_address,
                        "created_at": log.created_at.isoformat() if log.created_at else None,
                    }
                    for log in logs
                ],
                "page": page,
                "size": size,
                "total": total,
                "pages": max(1, (total + size - 1) // size),
            }
        }
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve audit logs: {str(e)}")


@router.get("/entity/{entity_type}/{entity_id}", response_model=dict,
             summary="Get entity audit history",
             description="Get complete audit trail for a specific entity")
async def get_entity_audit(
    entity_type: str,
    entity_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AuditService(db)
        logs = await service.get_entity_history(entity_type, entity_id)
        return {
            "success": True,
            "message": "Entity audit history retrieved",
            "data": {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entries": [
                    {
                        "id": log.id,
                        "action": log.action,
                        "user_id": log.user_id,
                        "old_values": log.old_values,
                        "new_values": log.new_values,
                        "metadata": log.log_metadata,
                        "created_at": log.created_at.isoformat() if log.created_at else None,
                    }
                    for log in logs
                ],
                "total": len(logs),
            }
        }
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve entity audit: {str(e)}")


@router.get("/stats", response_model=dict, summary="Audit log statistics",
             description="Get aggregated stats about audit log entries")
async def get_audit_stats(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AuditService(db)
        total = await service.count_logs()
        return {
            "success": True,
            "message": "Audit stats retrieved",
            "data": {"total_entries": total},
        }
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve audit stats: {str(e)}")
