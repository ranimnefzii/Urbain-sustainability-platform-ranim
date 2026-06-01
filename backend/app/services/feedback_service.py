import structlog
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.signal import Signal, SignalStatus
from app.models.user import User, UserRole
from app.services.audit_service import AuditService

logger = structlog.get_logger()

FEEDBACK_AUTO_REOPEN_THRESHOLD = 3


class FeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_feedback(
        self,
        signal_id: int,
        satisfaction: int,
        feedback: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        signal = await self.db.get(Signal, signal_id)
        if not signal:
            return {"reopened": False, "reason": "Signal not found"}

        if signal.status not in [SignalStatus.RESOLVED, SignalStatus.CLOSED]:
            return {"reopened": False, "reason": "Signal not in resolvable state"}

        if satisfaction < FEEDBACK_AUTO_REOPEN_THRESHOLD:
            signal.status = SignalStatus.UNDER_REVIEW
            signal.citizen_satisfaction = satisfaction
            signal.citizen_feedback = feedback or ""
            signal.internal_notes = (
                f"[{datetime.now(timezone.utc).isoformat()}] "
                f"Auto-reopened due to low satisfaction ({satisfaction}/5)"
            )
            await self.db.commit()

            await AuditService(self.db).log(
                action="signal.auto_reopened",
                entity_type="signal",
                entity_id=signal_id,
                user_id=user_id,
                new_values={
                    "citizen_satisfaction": satisfaction,
                    "citizen_feedback": feedback,
                    "new_status": SignalStatus.UNDER_REVIEW.value,
                },
                severity="warning",
                metadata={"reason": f"Low satisfaction ({satisfaction}/5 < {FEEDBACK_AUTO_REOPEN_THRESHOLD})"},
            )

            logger.info(
                "Signal auto-reopened due to low satisfaction",
                signal_id=signal_id,
                satisfaction=satisfaction,
            )

            return {
                "reopened": True,
                "reason": f"Low satisfaction ({satisfaction}/5) - signal reopened for review",
                "new_status": SignalStatus.UNDER_REVIEW.value,
            }

        return {"reopened": False, "reason": "Satisfaction meets threshold"}

    async def get_feedback_stats(self) -> dict:
        from sqlalchemy import func, and_

        query = select(
            func.avg(Signal.citizen_satisfaction).label("avg_satisfaction"),
            func.count(Signal.id).label("total_feedback"),
            func.sum(
                Signal.citizen_satisfaction.isnot(None).cast(type=type(func.count(1)))
            ).label("with_feedback"),
        ).where(
            Signal.citizen_satisfaction.isnot(None),
            Signal.status.in_([SignalStatus.RESOLVED, SignalStatus.CLOSED, SignalStatus.UNDER_REVIEW]),
        )
        result = await self.db.execute(query)
        row = result.one_or_none()

        return {
            "average_satisfaction": round(float(row[0]), 2) if row and row[0] else 0,
            "total_feedback_count": row[1] or 0,
            "auto_reopened_count": 0,
        }
