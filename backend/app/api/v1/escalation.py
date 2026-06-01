from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_admin, get_current_sector_user
from app.services.escalation_service import EscalationService
from app.core.exceptions import NotFoundError, BusinessLogicError, DatabaseError

router = APIRouter()


@router.get("/candidates", response_model=dict, summary="Get escalation candidates",
             description="List signals approaching or exceeding SLA thresholds")
async def get_escalation_candidates(
    priority_id: Optional[int] = Query(None, description="Filter by priority ID"),
    min_ratio: float = Query(0.8, ge=0.0, le=2.0, description="Minimum elapsed SLA ratio"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EscalationService(db)
        candidates = await service.get_escalation_candidates(
            priority_id=priority_id, min_ratio=min_ratio
        )
        return {
            "success": True,
            "message": f"{len(candidates)} escalation candidates found",
            "data": {"items": candidates, "total": len(candidates)}
        }
    except Exception as e:
        raise DatabaseError(f"Failed to get escalation candidates: {str(e)}")


@router.post("/{signal_id}/escalate", response_model=dict, summary="Escalate a signal",
              description="Escalate a signal to the next priority level")
async def escalate_signal(
    signal_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EscalationService(db)
        result = await service.escalate_signal(signal_id, current_user.id)
        return {"success": True, "message": "Signal escalated", "data": result}
    except (NotFoundError, BusinessLogicError):
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to escalate signal: {str(e)}")


@router.get("/sla-check/{signal_id}", response_model=dict, summary="Check SLA for a signal",
             description="Get SLA status for a specific signal")
async def check_sla(
    signal_id: int,
    current_user = Depends(get_current_sector_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EscalationService(db)
        result = await service.check_sla(signal_id)
        return {"success": True, "message": "SLA check complete", "data": result}
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to check SLA: {str(e)}")


@router.get("/summary", response_model=dict, summary="SLA summary",
             description="Get overall SLA compliance summary across all priorities")
async def get_sla_summary(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EscalationService(db)
        summary = await service.get_sla_summary()
        return {"success": True, "message": "SLA summary retrieved", "data": summary}
    except Exception as e:
        raise DatabaseError(f"Failed to get SLA summary: {str(e)}")
