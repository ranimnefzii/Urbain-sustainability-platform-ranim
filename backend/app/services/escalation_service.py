import structlog
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, or_

from app.models.signal import Signal, SignalStatus
from app.models.priority import Priority
from app.core.exceptions import NotFoundError, BusinessLogicError, DatabaseError

logger = structlog.get_logger()

SLA_STATES = {
    "NORMAL": {"color": "green", "label": "On Track", "threshold": 0.0},
    "WARNING": {"color": "yellow", "label": "At Risk", "threshold": 0.8},
    "BREACHED": {"color": "red", "label": "Breached", "threshold": 1.0},
    "ESCALATED": {"color": "purple", "label": "Escalated", "threshold": 1.2},
}


class EscalationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _compute_sla_state(self, signal: Signal, priority: Optional[Priority]) -> Tuple[str, float, float]:
        if not priority or not priority.sla_hours:
            return "NORMAL", 0.0, 0.0
        if signal.status in [SignalStatus.CLOSED, SignalStatus.RESOLVED, SignalStatus.CANCELLED, SignalStatus.REJECTED]:
            return "COMPLETED", 1.0, 0.0
        elapsed = (datetime.now(timezone.utc) - signal.created_at).total_seconds() / 3600
        ratio = elapsed / priority.sla_hours
        if ratio >= 1.2:
            return "ESCALATED", ratio, priority.sla_hours
        if ratio >= 1.0:
            return "BREACHED", ratio, priority.sla_hours
        if ratio >= 0.8:
            return "WARNING", ratio, priority.sla_hours
        return "NORMAL", ratio, priority.sla_hours

    async def check_sla(self, signal_id: int) -> Dict[str, Any]:
        signal = await self.db.get(Signal, signal_id)
        if not signal:
            raise NotFoundError(f"Signal {signal_id} not found")
        priority = await self.db.get(Priority, signal.priority_id) if signal.priority_id else None
        state, ratio, sla_hours = await self._compute_sla_state(signal, priority)
        return {
            "signal_id": signal.id,
            "reference_number": signal.reference_number,
            "priority_level": priority.level if priority else None,
            "sla_hours": sla_hours,
            "elapsed_ratio": round(ratio, 3),
            "state": state,
            "created_at": signal.created_at.isoformat(),
            "deadline": (signal.created_at + timedelta(hours=sla_hours)).isoformat() if sla_hours else None,
        }

    async def get_escalation_candidates(
        self, priority_id: Optional[int] = None, min_ratio: float = 0.8
    ) -> List[Dict[str, Any]]:
        query = select(Signal).where(
            Signal.status.in_([
                SignalStatus.SUBMITTED, SignalStatus.UNDER_REVIEW,
                SignalStatus.ASSIGNED, SignalStatus.IN_PROGRESS,
            ])
        )
        if priority_id:
            query = query.where(Signal.priority_id == priority_id)
        result = await self.db.execute(query)
        signals = result.scalars().all()

        candidates = []
        for sig in signals:
            priority = await self.db.get(Priority, sig.priority_id) if sig.priority_id else None
            state, ratio, sla_hours = await self._compute_sla_state(sig, priority)
            if ratio >= min_ratio:
                candidates.append({
                    "signal_id": sig.id,
                    "reference_number": sig.reference_number,
                    "title": sig.title,
                    "priority_level": priority.level if priority else None,
                    "sla_hours": sla_hours,
                    "elapsed_ratio": round(ratio, 3),
                    "state": state,
                    "created_at": sig.created_at.isoformat(),
                    "status": sig.status.value,
                })
        return sorted(candidates, key=lambda c: c["elapsed_ratio"], reverse=True)

    async def escalate_signal(self, signal_id: int, user_id: int) -> Dict[str, Any]:
        signal = await self.db.get(Signal, signal_id)
        if not signal:
            raise NotFoundError(f"Signal {signal_id} not found")
        if signal.status in [SignalStatus.CLOSED, SignalStatus.RESOLVED, SignalStatus.CANCELLED]:
            raise BusinessLogicError(f"Cannot escalate signal in status '{signal.status.value}'")

        priorities_result = await self.db.execute(
            select(Priority).order_by(Priority.priority_level.desc())
        )
        all_priorities = priorities_result.scalars().all()
        if not all_priorities:
            raise BusinessLogicError("No priorities configured for escalation")

        current_priority = await self.db.get(Priority, signal.priority_id) if signal.priority_id else None
        if current_priority:
            escalation_target = None
            for p in all_priorities:
                if p.priority_level > current_priority.priority_level:
                    escalation_target = p
                    break
            if escalation_target:
                signal.priority_id = escalation_target.id
                signal.escalation_notes = (
                    f"[{datetime.now(timezone.utc).isoformat()}] "
                    f"Escalated from {current_priority.name} to {escalation_target.name} by user {user_id}"
                )
            else:
                signal.escalation_notes = (
                    f"[{datetime.now(timezone.utc).isoformat()}] "
                    f"Already at highest priority; flagged for admin attention by user {user_id}"
                )
        else:
            signal.priority_id = all_priorities[0].id
            signal.escalation_notes = (
                f"[{datetime.now(timezone.utc).isoformat()}] "
                f"Assigned priority {all_priorities[0].name} and escalated by user {user_id}"
            )

        signal.last_activity_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(signal)

        return await self.check_sla(signal.id)

    async def get_sla_summary(self) -> Dict[str, Any]:
        priorities_result = await self.db.execute(
            select(Priority).where(Priority.is_active == True).order_by(Priority.priority_level)
        )
        priorities = priorities_result.scalars().all()

        total_signals = 0
        total_breached = 0
        total_warning = 0
        total_escalated = 0
        by_priority = []

        for p in priorities:
            query = select(Signal).where(
                Signal.priority_id == p.id,
                Signal.status.in_([
                    SignalStatus.SUBMITTED, SignalStatus.UNDER_REVIEW,
                    SignalStatus.ASSIGNED, SignalStatus.IN_PROGRESS,
                ])
            )
            result = await self.db.execute(query)
            sigs = result.scalars().all()

            breached = 0
            warning = 0
            escalated = 0
            for sig in sigs:
                state, ratio, _ = await self._compute_sla_state(sig, p)
                if state == "ESCALATED":
                    escalated += 1
                elif state == "BREACHED":
                    breached += 1
                elif state == "WARNING":
                    warning += 1

            total_signals += len(sigs)
            total_breached += breached
            total_warning += warning
            total_escalated += escalated

            by_priority.append({
                "priority_id": p.id,
                "name": p.name,
                "level": p.priority_level,
                "sla_hours": p.sla_hours,
                "total_active": len(sigs),
                "breached": breached,
                "warning": warning,
                "escalated": escalated,
                "breach_rate": round((breached / len(sigs) * 100), 1) if sigs else 0,
            })

        return {
            "total_active_signals": total_signals,
            "total_breached": total_breached,
            "total_warning": total_warning,
            "total_escalated": total_escalated,
            "overall_breach_rate": round((total_breached / total_signals * 100), 1) if total_signals else 0,
            "by_priority": by_priority,
        }
