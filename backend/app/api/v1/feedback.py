from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.services.feedback_service import FeedbackService
from app.core.exceptions import BusinessLogicError

router = APIRouter()


@router.post("/{signal_id}/process", response_model=dict, summary="Process citizen feedback",
              description="Process citizen feedback with auto-reopen for low satisfaction")
async def process_feedback(
    signal_id: int,
    satisfaction: int,
    feedback: str = "",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = FeedbackService(db)
        result = await service.process_feedback(
            signal_id=signal_id,
            satisfaction=satisfaction,
            feedback=feedback,
            user_id=current_user.id,
        )
        return {"success": True, "message": "Feedback processed", "data": result}
    except Exception as e:
        raise BusinessLogicError(f"Failed to process feedback: {str(e)}")


@router.get("/stats", response_model=dict, summary="Get feedback stats",
              description="Get aggregated citizen feedback statistics")
async def get_feedback_stats(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = FeedbackService(db)
        stats = await service.get_feedback_stats()
        return {"success": True, "message": "Feedback stats retrieved", "data": stats}
    except Exception as e:
        raise BusinessLogicError(f"Failed to get feedback stats: {str(e)}")
