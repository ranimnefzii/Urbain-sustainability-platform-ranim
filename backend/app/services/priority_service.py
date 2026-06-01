"""
Priority Service - Urbain Sustainability System
Service métier pour la gestion des priorités et l'évaluation des signalements
"""

import structlog
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, or_

from app.services.base import BaseService
from app.models.priority import (
    Priority, PriorityLevel, SeverityLevel, UrgencyLevel, ImpactLevel
)
from app.models.signal import Signal, SignalStatus
from app.schemas.priority import PriorityCreate, PriorityUpdate
from app.repositories import PriorityRepository, SignalRepository
from app.core.exceptions import (
    DatabaseError, NotFoundError, ValidationError,
    BusinessLogicError, ConflictError
)

logger = structlog.get_logger()


class PriorityService(BaseService[Priority, PriorityCreate, PriorityUpdate]):
    """
    Service métier pour la gestion des priorités des signalements
    Calcule les scores, détecte les escalades et évalue la criticité
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = PriorityRepository(db, Priority)

    async def create_priority(self, obj_in: PriorityCreate) -> Priority:
        try:
            code_exists = await self.repository.check_code_exists(code=obj_in.code)
            if code_exists:
                raise ConflictError(f"Priority code '{obj_in.code}' already exists")

            name_exists = await self.repository.check_name_exists(name=obj_in.name)
            if name_exists:
                raise ConflictError(f"Priority name '{obj_in.name}' already exists")

            existing_level = await self.repository.get_by_level(
                priority_level=PriorityLevel(obj_in.priority_level)
            )
            if existing_level:
                raise ConflictError(
                    f"A priority with level {obj_in.priority_level} already exists: '{existing_level.name}'"
                )

            obj_data = obj_in.model_dump()
            obj_data["priority_level"] = PriorityLevel(obj_in.priority_level)
            obj_data["severity_level"] = SeverityLevel(obj_in.severity_level)
            obj_data["urgency_level"] = UrgencyLevel(obj_in.urgency_level)
            obj_data["impact_level"] = ImpactLevel(obj_in.impact_level)
            priority = Priority(**obj_data)
            self.db.add(priority)
            await self.db.commit()
            await self.db.refresh(priority)

            await self.log_operation("create_priority", {"priority_id": priority.id, "code": priority.code})
            return priority
        except ConflictError:
            raise
        except Exception as e:
            await self.log_error("create_priority", e)
            raise DatabaseError(f"Failed to create priority: {str(e)}")

    async def get_priority(self, priority_id: int) -> Priority:
        try:
            priority = await self.repository.get(id=priority_id)
            if not priority:
                raise NotFoundError(f"Priority with id {priority_id} not found")
            return priority
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_priority", e, {"priority_id": priority_id})
            raise DatabaseError(f"Failed to get priority: {str(e)}")

    async def update_priority(self, priority_id: int, obj_in: PriorityUpdate) -> Priority:
        try:
            priority = await self.get_priority(priority_id)
            update_data = obj_in.model_dump(exclude_unset=True)

            if "code" in update_data:
                code_exists = await self.repository.check_code_exists(
                    code=update_data["code"], exclude_id=priority_id
                )
                if code_exists:
                    raise ConflictError(f"Priority code '{update_data['code']}' already exists")

            if "priority_level" in update_data:
                existing = await self.repository.get_by_level(
                    priority_level=PriorityLevel(update_data["priority_level"])
                )
                if existing and existing.id != priority_id:
                    raise ConflictError(
                        f"A priority with level {update_data['priority_level']} already exists"
                    )

            for field, value in update_data.items():
                if hasattr(priority, field):
                    setattr(priority, field, value)

            await self.db.commit()
            await self.db.refresh(priority)

            await self.log_operation("update_priority", {"priority_id": priority_id})
            return priority
        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            await self.log_error("update_priority", e, {"priority_id": priority_id})
            raise DatabaseError(f"Failed to update priority: {str(e)}")

    async def delete_priority(self, priority_id: int) -> bool:
        try:
            priority = await self.get_priority(priority_id)

            from app.models.signal import Signal
            signal_count_query = select(func.count(Signal.id)).where(Signal.priority_id == priority_id)
            signal_count_result = await self.db.execute(signal_count_query)
            if signal_count_result.scalar() > 0:
                raise BusinessLogicError(
                    "Cannot delete priority with associated signals. "
                    "Reassign signals to another priority first."
                )

            await self.repository.remove(id=priority_id)
            await self.log_operation("delete_priority", {"priority_id": priority_id})
            return True
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("delete_priority", e, {"priority_id": priority_id})
            raise DatabaseError(f"Failed to delete priority: {str(e)}")

    async def get_priorities(self, skip: int = 0, limit: int = 100,
                              filters: Optional[Dict[str, Any]] = None) -> List[Priority]:
        try:
            return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)
        except Exception as e:
            await self.log_error("get_priorities", e)
            raise DatabaseError(f"Failed to get priorities: {str(e)}")

    async def calculate_signal_priority(self, signal_id: int) -> Tuple[Priority, float]:
        try:
            from app.models.signal import Signal, SignalStatus
            from app.models.category import Category

            signal_query = select(Signal).where(Signal.id == signal_id)
            signal_result = await self.db.execute(signal_query)
            signal = signal_result.scalar_one_or_none()

            if not signal:
                raise NotFoundError(f"Signal with id {signal_id} not found")

            category_query = select(Category).where(Category.id == signal.category_id)
            category_result = await self.db.execute(category_query)
            category = category_result.scalar_one_or_none()

            severity = SeverityLevel.MODERATE
            urgency = UrgencyLevel.NORMAL
            impact = ImpactLevel.LOCAL

            if category:
                severity_map = {1: SeverityLevel.EXTREME, 2: SeverityLevel.SEVERE,
                               3: SeverityLevel.MODERATE, 4: SeverityLevel.MINOR, 5: SeverityLevel.NONE}
                severity = severity_map.get(category.default_severity_level, SeverityLevel.MODERATE)

            if signal.safety_risk_level:
                if signal.safety_risk_level >= 4:
                    urgency = UrgencyLevel.IMMEDIATE
                    severity = SeverityLevel.EXTREME
                elif signal.safety_risk_level >= 3:
                    urgency = UrgencyLevel.URGENT
                    severity = SeverityLevel.SEVERE

            if signal.estimated_damage_cost:
                if signal.estimated_damage_cost > 50000:
                    impact = ImpactLevel.WIDESPREAD
                elif signal.estimated_damage_cost > 10000:
                    impact = ImpactLevel.NEIGHBORHOOD

            if signal.affected_people_count:
                if signal.affected_people_count > 100:
                    impact = ImpactLevel.WIDESPREAD
                elif signal.affected_people_count > 20:
                    impact = ImpactLevel.NEIGHBORHOOD

            priorities = await self.repository.get_priorities_by_matrix(
                severity=severity, urgency=urgency
            )

            best_priority = None
            best_score = 0

            for p in priorities:
                base_score = 5.0
                score = p.calculate_priority_score(base_score)
                factor_map = {
                    ImpactLevel.WIDESPREAD: 0.5, ImpactLevel.NEIGHBORHOOD: 0.3,
                    ImpactLevel.LOCAL: 0.1, ImpactLevel.INDIVIDUAL: 0.0, ImpactLevel.NONE: -0.1
                }
                impact_factor = factor_map.get(impact, 0.1)
                adjusted_score = score * (1 + impact_factor)

                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_priority = p

            if best_priority:
                signal.priority_id = best_priority.id
                if best_score >= 7:
                    priority_enum = best_priority.priority_level
                    if priority_enum in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]:
                        signal.status = SignalStatus.UNDER_REVIEW

                await self.db.commit()
                return best_priority, best_score

            default = await self.repository.get_by_level(priority_level=PriorityLevel.MEDIUM)
            if default:
                signal.priority_id = default.id
                await self.db.commit()
                return default, 3.0

            raise BusinessLogicError("No suitable priority level found")
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("calculate_signal_priority", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to calculate signal priority: {str(e)}")

    async def get_priority_stats(self, priority_id: int) -> Dict[str, Any]:
        try:
            priority = await self.get_priority(priority_id)
            stats = await self.repository.get_priority_statistics(priority_id=priority_id)

            from app.models.signal import Signal
            category_query = select(
                Signal.category_id, func.count(Signal.id).label("count")
            ).where(
                Signal.priority_id == priority_id
            ).group_by(Signal.category_id)
            category_result = await self.db.execute(category_query)
            stats["signals_by_category"] = {row.category_id: row.count for row in category_result}

            return stats
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_priority_stats", e, {"priority_id": priority_id})
            raise DatabaseError(f"Failed to get priority stats: {str(e)}")

    async def get_priorities_by_level(self, level: int) -> List[Priority]:
        try:
            pl = PriorityLevel(level)
            priority = await self.repository.get_by_level(priority_level=pl)
            return [priority] if priority else []
        except Exception as e:
            await self.log_error("get_priorities_by_level", e, {"level": level})
            raise DatabaseError(f"Failed to get priorities by level: {str(e)}")

    async def assess_priority(self, signal_id: int) -> Dict[str, Any]:
        try:
            priority, score = await self.calculate_signal_priority(signal_id)

            priority_enum = priority.priority_level
            severity_enum = priority.severity_level
            urgency_enum = priority.urgency_level

            factors = {
                "priority_level": priority_enum.value,
                "severity_level": severity_enum.value,
                "urgency_level": urgency_enum.value,
                "impact_level": priority.impact_level.value,
                "ai_weight": priority.ai_weight,
                "calculated_score": round(score, 2),
                "max_response_time_minutes": priority.max_response_time_minutes,
                "max_resolution_time_hours": priority.max_resolution_time_hours,
                "requires_human_review": priority.requires_human_review,
                "escalation_enabled": priority.escalation_enabled
            }

            reasoning = []
            if score >= 7:
                reasoning.append("High priority score requires immediate attention")
            elif score >= 4:
                reasoning.append("Moderate priority score, standard processing")
            else:
                reasoning.append("Low priority score, routine processing")

            if priority.requires_human_review:
                reasoning.append("Requires human review based on priority configuration")

            recommended_action = "immediate_response" if priority.is_critical else \
                "expedited_processing" if priority.is_high_priority else "standard_processing"

            return {
                "signal_id": signal_id,
                "current_priority": priority.name,
                "suggested_priority": priority.name,
                "suggested_priority_id": priority.id,
                "confidence_score": min(1.0, score / 10.0),
                "assessment_factors": factors,
                "reasoning": "; ".join(reasoning),
                "recommended_action": recommended_action,
                "estimated_resolution_time_hours": priority.max_resolution_time_hours,
                "requires_escalation": priority.escalation_enabled and score >= 7
            }
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("assess_priority", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to assess priority: {str(e)}")

    async def get_escalation_candidates(self) -> List[Dict[str, Any]]:
        try:
            now = datetime.now(timezone.utc)
            candidates = []

            from app.models.signal import Signal
            active_signals_query = select(Signal).where(
                Signal.status.in_([
                    SignalStatus.SUBMITTED, SignalStatus.UNDER_REVIEW,
                    SignalStatus.ASSIGNED, SignalStatus.IN_PROGRESS
                ])
            )
            active_result = await self.db.execute(active_signals_query)
            active_signals = active_result.scalars().all()

            for signal in active_signals:
                priority = await self.repository.get(id=signal.priority_id)
                if not priority or not priority.escalation_enabled:
                    continue

                if priority.should_escalate(now, signal.created_at):
                    candidates.append({
                        "signal_id": signal.id,
                        "reference_number": signal.reference_number,
                        "title": signal.title,
                        "current_status": signal.status.value,
                        "priority_name": priority.name,
                        "priority_level": priority.priority_level.value,
                        "created_at": signal.created_at.isoformat(),
                        "escalation_deadline": priority.get_escalation_deadline(
                            signal.created_at
                        ).isoformat(),
                        "escalation_time_hours": priority.escalation_time_hours,
                        "overdue_by_hours": (now - priority.get_escalation_deadline(
                            signal.created_at
                        )).total_seconds() / 3600,
                        "assigned_sector_id": signal.assigned_sector_id,
                        "is_critical": priority.is_critical
                    })

            candidates.sort(
                key=lambda x: (x["priority_level"], -x["overdue_by_hours"])
            )

            return candidates
        except Exception as e:
            await self.log_error("get_escalation_candidates", e)
            raise DatabaseError(f"Failed to get escalation candidates: {str(e)}")
