"""
Signal Service - Urbain Sustainability System
Service métier pour la gestion des signalements
"""

import uuid
import structlog
import math
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, or_
from sqlalchemy.orm import selectinload

from app.services.base import BaseService
from app.models.signal import Signal, SignalStatus, SignalSource, VerificationStatus
from app.models.user import User, UserRole
from app.schemas.signal import SignalCreate, SignalUpdate
from app.repositories import SignalRepository, UserRepository
from app.core.exceptions import (
    DatabaseError, NotFoundError, ValidationError,
    BusinessLogicError, AuthorizationError, ConflictError, ExternalServiceError
)
from app.core.transaction import transactional
from app.services.audit_service import AuditService

logger = structlog.get_logger()

VALID_TRANSITIONS = {
    SignalStatus.DRAFT: [SignalStatus.SUBMITTED],
    SignalStatus.SUBMITTED: [SignalStatus.UNDER_REVIEW, SignalStatus.CANCELLED],
    SignalStatus.UNDER_REVIEW: [SignalStatus.ASSIGNED, SignalStatus.REJECTED, SignalStatus.CANCELLED],
    SignalStatus.ASSIGNED: [SignalStatus.IN_PROGRESS, SignalStatus.UNDER_REVIEW],
    SignalStatus.IN_PROGRESS: [SignalStatus.RESOLVED, SignalStatus.UNDER_REVIEW],
    SignalStatus.RESOLVED: [SignalStatus.CLOSED],
    SignalStatus.CLOSED: [],
    SignalStatus.CANCELLED: [],
    SignalStatus.REJECTED: []
}


class SignalService(BaseService[Signal, SignalCreate, SignalUpdate]):
    """
    Service métier pour la gestion des signalements de problèmes urbains
    Gère le cycle de vie complet, les transitions d'état et l'intégration IA
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = SignalRepository(db, Signal)

    async def _validate_status_transition(self, current: SignalStatus, new: SignalStatus) -> None:
        if current == new:
            raise BusinessLogicError(f"Signal is already in status {current.value}")
        allowed = VALID_TRANSITIONS.get(current, [])
        if new not in allowed:
            raise BusinessLogicError(
                f"Cannot transition from {current.value} to {new.value}. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )

    async def _generate_reference_number(self) -> str:
        year = datetime.now().strftime("%Y")
        month = datetime.now().strftime("%m")
        unique = str(uuid.uuid4())[:6].upper()
        return f"SIG-{year}{month}-{unique}"

    async def _run_ai_classification(self, signal: Signal) -> Signal:
        try:
            from app.services.ai_service import AIService
            ai_service = AIService(self.db)
            text_content = f"{signal.title} {signal.description}"
            result = await ai_service.classify_signal(text_content)
            if result:
                signal.ai_confidence_score = result.get("confidence_score")
                signal.ai_classification = result.get("classification")
                signal.ai_priority_score = result.get("priority_score")
                signal.ai_severity_score = result.get("severity_score")
                signal.ai_urgency_score = result.get("urgency_score")
                signal.ai_processing_time_ms = result.get("processing_time_ms")
                await self.db.commit()
            return signal
        except Exception as e:
            logger.warning("AI classification failed", signal_id=signal.id, error=str(e))
            return signal

    async def _send_status_notification(self, signal: Signal, old_status: SignalStatus) -> None:
        try:
            from app.services.notification_service import NotificationService
            from app.schemas.notification import NotificationCreate
            from app.models.notification import NotificationType, NotificationChannel, NotificationPriority

            notif_service = NotificationService(self.db)

            type_map = {
                SignalStatus.SUBMITTED: NotificationType.SIGNAL_CREATED,
                SignalStatus.ASSIGNED: NotificationType.SIGNAL_ASSIGNED,
                SignalStatus.RESOLVED: NotificationType.SIGNAL_RESOLVED,
                SignalStatus.IN_PROGRESS: NotificationType.SIGNAL_UPDATED,
            }
            notif_type = type_map.get(signal.status, NotificationType.SIGNAL_UPDATED)

            user = await self.db.get(User, signal.created_by)
            if user:
                notif_data = NotificationCreate(
                    title=f"Signal {signal.reference_number} - {signal.status.value}",
                    message=f"Your signal '{signal.title}' has changed from {old_status.value} to {signal.status.value}",
                    notification_type=notif_type.value,
                    channel="in_app",
                    user_id=user.id,
                    signal_id=signal.id,
                    priority="high" if signal.status in [SignalStatus.ASSIGNED, SignalStatus.RESOLVED] else "normal"
                )
                await notif_service.create_notification(notif_data)
        except Exception as e:
            logger.warning("Failed to send status notification", signal_id=signal.id, error=str(e))

    async def create_signal(self, obj_in: SignalCreate, user_id: int) -> Signal:
        try:
            obj_data = obj_in.model_dump()
            location = obj_data.pop("location", {})

            ref_number = await self._generate_reference_number()

            signal = Signal(
                title=obj_data["title"],
                description=obj_data["description"],
                reference_number=ref_number,
                created_by=user_id,
                category_id=obj_data["category_id"],
                priority_id=1,
                latitude=location.get("latitude"),
                longitude=location.get("longitude"),
                address=location.get("address"),
                postal_code=location.get("postal_code"),
                city=location.get("city"),
                country=location.get("country", "Tunisia"),
                location_accuracy=location.get("location_accuracy"),
                location_description=location.get("location_description"),
                images=obj_data.get("images"),
                videos=obj_data.get("videos"),
                documents=obj_data.get("documents"),
                audio_files=obj_data.get("audio_files"),
                is_anonymous=obj_data.get("is_anonymous", False),
                allow_contact=obj_data.get("allow_contact", True),
                estimated_damage_cost=obj_data.get("estimated_damage_cost"),
                affected_people_count=obj_data.get("affected_people_count"),
                affected_area_sqm=obj_data.get("affected_area_sqm"),
                safety_risk_level=obj_data.get("safety_risk_level"),
                source=SignalSource.WEB,
                status=SignalStatus.DRAFT,
                verification_status=VerificationStatus.PENDING
            )

            self.db.add(signal)
            await self.db.commit()
            await self.db.refresh(signal)

            signal =             signal = await self._run_ai_classification(signal)

            from app.models.user import User
            user = await self.db.get(User, user_id)
            if user:
                user.total_signals_created += 1
                await self.db.commit()

            signal = await self.repository.get_signal_with_relations(signal_id=signal.id)

            await self.log_operation("create_signal", {"signal_id": signal.id, "ref": ref_number})
            await AuditService(self.db).log_entity_crud(
                action="create", entity_type="signal",
                entity_id=signal.id, user_id=user_id,
                new_values={"reference_number": ref_number, "title": signal.title, "status": signal.status.value},
            )
            return signal
        except Exception as e:
            await self.log_error("create_signal", e)
            raise DatabaseError(f"Failed to create signal: {str(e)}")

    async def get_signal(self, signal_id: int) -> Signal:
        try:
            signal = await self.repository.get_signal_with_relations(signal_id=signal_id)
            if not signal:
                raise NotFoundError(f"Signal with id {signal_id} not found")
            return signal
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to get signal: {str(e)}")

    async def update_signal(self, signal_id: int, obj_in: SignalUpdate, user_id: int) -> Signal:
        try:
            signal = await self.get_signal(signal_id)

            if not signal.can_be_edited_by_user(user_id):
                current_user = await self.db.get(User, user_id)
                if not current_user or current_user.role not in [UserRole.ADMIN, UserRole.SECTOR]:
                    raise AuthorizationError("Not authorized to update this signal")

            update_data = obj_in.model_dump(exclude_unset=True)

            if "location" in update_data:
                location = update_data.pop("location")
                for key, value in location.items():
                    if hasattr(signal, key) and value is not None:
                        setattr(signal, key, value)

            for field, value in update_data.items():
                if hasattr(signal, field) and value is not None:
                    setattr(signal, field, value)

            signal.updated_at = datetime.now(timezone.utc)
            signal.last_activity_at = datetime.now(timezone.utc)

            await self.db.commit()
            await self.db.refresh(signal)

            await self.log_operation("update_signal", {"signal_id": signal_id, "user_id": user_id})
            return signal
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            await self.log_error("update_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to update signal: {str(e)}")

    async def delete_signal(self, signal_id: int, user_id: int) -> bool:
        try:
            signal = await self.get_signal(signal_id)
            current_user = await self.db.get(User, user_id)

            if signal.created_by != user_id:
                if not current_user or current_user.role != UserRole.ADMIN:
                    raise AuthorizationError("Not authorized to delete this signal")

            if signal.status not in [SignalStatus.DRAFT, SignalStatus.CANCELLED, SignalStatus.REJECTED]:
                raise BusinessLogicError("Cannot delete a signal that is in active processing state")

            signal.soft_delete()
            await self.db.commit()

            await AuditService(self.db).log_entity_crud(
                action="delete", entity_type="signal",
                entity_id=signal_id, user_id=user_id,
                old_values={"reference_number": signal.reference_number, "title": signal.title},
            )
            return True
        except (NotFoundError, AuthorizationError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("delete_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to delete signal: {str(e)}")

    async def restore_signal(self, signal_id: int, user_id: int) -> Signal:
        try:
            signal = await self.get_signal(signal_id)
            if not signal.is_deleted:
                raise BusinessLogicError("Signal is not deleted")
            current_user = await self.db.get(User, user_id)
            if not current_user or current_user.role != UserRole.ADMIN:
                raise AuthorizationError("Only admins can restore signals")
            signal.restore()
            await self.db.commit()
            await AuditService(self.db).log_entity_crud(
                action="restore", entity_type="signal",
                entity_id=signal_id, user_id=user_id,
                new_values={"reference_number": signal.reference_number},
            )
            return signal
        except (NotFoundError, AuthorizationError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("restore_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to restore signal: {str(e)}")

    async def get_signals(self, skip: int = 0, limit: int = 100,
                          filters: Optional[Dict[str, Any]] = None) -> List[Signal]:
        try:
            if filters:
                search_term = filters.pop("search", None) if filters else None
                sort_by = filters.pop("sort_by", None) if filters else None
                sort_order = filters.pop("sort_order", None) if filters else None
                date_from = filters.pop("start_date", None) if filters else None
                date_to = filters.pop("end_date", None) if filters else None
                assigned_to = filters.pop("assigned_to", None) if filters else None

                if assigned_to:
                    filters["assigned_to"] = assigned_to

                if search_term:
                    return await self.repository.search_signals(
                        search_term=search_term, skip=skip, limit=limit
                    )

                return await self.repository.get_multi(
                    skip=skip, limit=limit, filters=filters,
                    order_by=sort_by, sort_order=sort_order
                )
            return await self.repository.get_multi(skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("get_signals", e)
            raise DatabaseError(f"Failed to get signals: {str(e)}")

    async def search_signals(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Signal]:
        try:
            return await self.repository.search_signals(search_term=search_term, skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("search_signals", e, {"search_term": search_term})
            raise DatabaseError(f"Failed to search signals: {str(e)}")

    async def get_nearby_signals(self, latitude: float, longitude: float,
                                  radius_km: float = 5.0, skip: int = 0, limit: int = 100) -> List[Signal]:
        try:
            await self.validate_required_fields(
                {"latitude": latitude, "longitude": longitude},
                ["latitude", "longitude"]
            )
            return await self.repository.get_signals_near_location(
                latitude=latitude, longitude=longitude,
                radius_km=radius_km, skip=skip, limit=limit
            )
        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("get_nearby_signals", e)
            raise DatabaseError(f"Failed to get nearby signals: {str(e)}")

    async def assign_signal(self, signal_id: int, user_id: int,
                             sector_id: Optional[int] = None, assigned_by: int = 0) -> Signal:
        try:
            signal = await self.get_signal(signal_id)

            await self._validate_status_transition(signal.status, SignalStatus.ASSIGNED)

            target_user = await self.db.get(User, user_id)
            if not target_user:
                raise NotFoundError(f"User with id {user_id} not found")
            if not target_user.can_process_signals():
                raise BusinessLogicError("Target user cannot process signals")

            success = await self.repository.assign_to_user(
                signal_id=signal_id, user_id=user_id, sector_id=sector_id
            )
            if not success:
                raise DatabaseError("Failed to assign signal")

            await self.db.refresh(signal)

            await self.log_operation("assign_signal", {
                "signal_id": signal_id, "user_id": user_id, "sector_id": sector_id
            })
            return signal
        except (NotFoundError, BusinessLogicError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("assign_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to assign signal: {str(e)}")

    async def process_signal(self, signal_id: int, new_status: SignalStatus,
                              user_id: int, notes: Optional[str] = None) -> Signal:
        try:
            signal = await self.get_signal(signal_id)

            await self._validate_status_transition(signal.status, new_status)

            current_user = await self.db.get(User, user_id)
            if not current_user or not current_user.can_process_signals():
                raise AuthorizationError("Not authorized to process signals")

            old_status = signal.status
            signal.update_status(new_status, user_id=user_id, notes=notes)
            signal.updated_at = datetime.now(timezone.utc)
            signal.last_activity_at = datetime.now(timezone.utc)

            if new_status == SignalStatus.RESOLVED:
                current_user.total_signals_processed += 1

            await self.db.commit()
            await self.db.refresh(signal)

            await self._send_status_notification(signal, old_status)

            signal = await self.repository.get_signal_with_relations(signal_id=signal.id)

            await AuditService(self.db).log_state_change(
                entity_type="signal", entity_id=signal_id,
                from_state=old_status.value, to_state=new_status.value,
                user_id=user_id,
                metadata={"reference_number": signal.reference_number, "title": signal.title},
            )

            await self.log_operation("process_signal", {
                "signal_id": signal_id, "from": old_status.value, "to": new_status.value
            })
            return signal
        except (NotFoundError, BusinessLogicError, AuthorizationError):
            raise
        except Exception as e:
            await self.log_error("process_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to process signal: {str(e)}")

    async def resolve_signal(self, signal_id: int, user_id: int,
                              resolution_description: str, resolution_method: Optional[str] = None,
                              resolution_cost: Optional[float] = None) -> Signal:
        try:
            return await self.process_signal(
                signal_id=signal_id, new_status=SignalStatus.RESOLVED,
                user_id=user_id, notes=resolution_description
            )
        except Exception as e:
            await self.log_error("resolve_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to resolve signal: {str(e)}")

    async def cancel_signal(self, signal_id: int, user_id: int, reason: Optional[str] = None) -> Signal:
        try:
            signal = await self.get_signal(signal_id)
            if signal.created_by != user_id:
                current_user = await self.db.get(User, user_id)
                if not current_user or current_user.role not in [UserRole.ADMIN, UserRole.SECTOR]:
                    raise AuthorizationError("Not authorized to cancel this signal")

            return await self.process_signal(
                signal_id=signal_id, new_status=SignalStatus.CANCELLED,
                user_id=user_id, notes=reason
            )
        except (NotFoundError, AuthorizationError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("cancel_signal", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to cancel signal: {str(e)}")

    async def get_signal_stats(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            return await self.repository.get_signal_statistics(filters=filters)
        except Exception as e:
            await self.log_error("get_signal_stats", e)
            raise DatabaseError(f"Failed to get signal stats: {str(e)}")

    async def get_user_signals(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Signal]:
        try:
            return await self.repository.get_by_user(user_id=user_id, skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("get_user_signals", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to get user signals: {str(e)}")

    async def get_sector_signals(self, sector_id: int, skip: int = 0, limit: int = 100) -> List[Signal]:
        try:
            return await self.repository.get_signals_with_filters(
                filters={"assigned_sector_id": sector_id}, skip=skip, limit=limit
            )
        except Exception as e:
            await self.log_error("get_sector_signals", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to get sector signals: {str(e)}")

    async def submit_feedback(self, signal_id: int, user_id: int,
                                 satisfaction: int, feedback: Optional[str] = None) -> Signal:
        try:
            signal = await self.get_signal(signal_id)

            if signal.created_by != user_id:
                current_user = await self.db.get(User, user_id)
                if not current_user or current_user.role not in [UserRole.ADMIN, UserRole.SECTOR]:
                    raise AuthorizationError("Not authorized to submit feedback for this signal")

            if signal.status not in [SignalStatus.RESOLVED, SignalStatus.CLOSED]:
                raise BusinessLogicError("Feedback can only be submitted for resolved or closed signals")

            signal.citizen_satisfaction = satisfaction
            if feedback:
                signal.citizen_feedback = feedback
            signal.updated_at = datetime.now(timezone.utc)
            signal.last_activity_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(signal)

            await AuditService(self.db).log(
                action="signal.submit_feedback", entity_type="signal",
                entity_id=signal_id, user_id=user_id,
                new_values={"citizen_satisfaction": satisfaction, "citizen_feedback": feedback},
                severity="info",
            )
            await self.log_operation("submit_feedback", {"signal_id": signal_id, "satisfaction": satisfaction})
            return signal
        except (NotFoundError, AuthorizationError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("submit_feedback", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to submit feedback: {str(e)}")

    async def add_media(self, signal_id: int, media_type: str,
                         media_urls: List[str], user_id: int) -> Signal:
        try:
            signal = await self.get_signal(signal_id)

            if signal.created_by != user_id:
                current_user = await self.db.get(User, user_id)
                if not current_user or current_user.role not in [UserRole.ADMIN, UserRole.SECTOR]:
                    raise AuthorizationError("Not authorized to add media to this signal")

            if media_type == "images":
                current = signal.images or []
                signal.images = current + media_urls
            elif media_type == "videos":
                current = signal.videos or []
                signal.videos = current + media_urls
            elif media_type == "documents":
                current = signal.documents or []
                signal.documents = current + media_urls
            elif media_type == "audio":
                current = signal.audio_files or []
                signal.audio_files = current + media_urls
            else:
                raise ValidationError(f"Invalid media type: {media_type}")

            signal.updated_at = datetime.now(timezone.utc)
            signal.last_activity_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(signal)

            await self.log_operation("add_media", {"signal_id": signal_id, "media_type": media_type})
            return signal
        except (NotFoundError, AuthorizationError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("add_media", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to add media: {str(e)}")

    async def get_signal_timeline(self, signal_id: int) -> List[Dict[str, Any]]:
        try:
            signal = await self.get_signal(signal_id)
            timeline = []

            timeline.append({
                "type": "created",
                "status": SignalStatus.DRAFT.value,
                "timestamp": signal.created_at.isoformat(),
                "description": "Signal created"
            })

            if signal.submitted_at:
                timeline.append({
                    "type": "submitted",
                    "status": SignalStatus.SUBMITTED.value,
                    "timestamp": signal.submitted_at.isoformat() if hasattr(signal, 'submitted_at') else None,
                    "description": "Signal submitted"
                })

            if signal.assigned_at:
                timeline.append({
                    "type": "assigned",
                    "status": SignalStatus.ASSIGNED.value,
                    "timestamp": signal.assigned_at.isoformat(),
                    "description": f"Assigned to user {signal.processed_by}"
                })

            if signal.started_processing_at:
                timeline.append({
                    "type": "processing",
                    "status": SignalStatus.IN_PROGRESS.value,
                    "timestamp": signal.started_processing_at.isoformat(),
                    "description": "Processing started"
                })

            if signal.resolved_at:
                timeline.append({
                    "type": "resolved",
                    "status": SignalStatus.RESOLVED.value,
                    "timestamp": signal.resolved_at.isoformat(),
                    "description": signal.resolution_description or "Signal resolved"
                })

            if signal.closed_at:
                timeline.append({
                    "type": "closed",
                    "status": SignalStatus.CLOSED.value,
                    "timestamp": signal.closed_at.isoformat(),
                    "description": "Signal closed"
                })

            timeline.sort(key=lambda x: x.get("timestamp") or "")
            return timeline
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_signal_timeline", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to get signal timeline: {str(e)}")
