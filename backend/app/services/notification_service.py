"""
Notification Service - Urbain Sustainability System
Service métier pour la gestion des notifications et alertes
"""

import uuid
import structlog
import math
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, or_

from app.services.base import BaseService
from app.models.notification import (
    Notification, NotificationType, NotificationChannel,
    NotificationPriority, NotificationStatus
)
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.repositories import NotificationRepository
from app.core.exceptions import (
    DatabaseError, NotFoundError, ValidationError,
    BusinessLogicError, ExternalServiceError, AuthorizationError
)

logger = structlog.get_logger()


class NotificationService(BaseService[Notification, NotificationCreate, NotificationUpdate]):
    """
    Service métier pour la gestion des notifications et alertes système
    Gère l'envoi multi-canal, les templates, les retries et la planification
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = NotificationRepository(db, Notification)

    async def _generate_notification_code(self, notification_type: NotificationType) -> str:
        year = datetime.now().strftime("%Y")
        month = datetime.now().strftime("%m")
        type_prefix = notification_type.value[:3].upper()
        unique = str(uuid.uuid4())[:4].upper()
        return f"NOT-{type_prefix}-{year}{month}-{unique}"

    async def _render_template(self, notification: Notification) -> Notification:
        if notification.template_name and notification.template_variables:
            title = notification.title
            message = notification.message
            for key, value in notification.template_variables.items():
                placeholder = f"{{{key}}}"
                title = title.replace(placeholder, str(value))
                message = message.replace(placeholder, str(value))
            notification.title = title
            notification.message = message
        return notification

    async def _deliver_via_channel(self, notification: Notification) -> Notification:
        try:
            notification.mark_as_sent()

            channel = notification.channel
            if channel == NotificationChannel.EMAIL:
                if notification.recipient_email:
                    from app.services.email_service import EmailService
                    email_service = EmailService(self.db)
                    await email_service.send_email(
                        to_email=notification.recipient_email,
                        subject=notification.title,
                        html_content=notification.message
                    )
            elif channel == NotificationChannel.WHATSAPP:
                if notification.recipient_phone:
                    from app.services.whatsapp_service import WhatsAppService
                    wa_service = WhatsAppService(self.db)
                    await wa_service.send_whatsapp(
                        to_phone=notification.recipient_phone,
                        message=notification.message,
                        user_id=notification.user_id,
                        signal_id=notification.signal_id
                    )
            elif channel == NotificationChannel.PUSH:
                if notification.recipient_device_token:
                    from app.services.push_service import PushService
                    push_service = PushService(self.db)
                    await push_service.send_push(
                        token=notification.recipient_device_token,
                        title=notification.title,
                        body=notification.message
                    )
            elif channel == NotificationChannel.IN_APP:
                pass
            elif channel == NotificationChannel.WEBHOOK:
                if notification.recipient_webhook_url:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            notification.recipient_webhook_url,
                            json={"title": notification.title, "message": notification.message}
                        )

            notification.mark_as_delivered({"channel": channel.value, "timestamp": datetime.now(timezone.utc).isoformat()})
            await self.db.commit()
            return notification
        except Exception as e:
            logger.error("Channel delivery failed", channel=notification.channel.value, error=str(e))
            notification.mark_as_failed(str(e))
            await self.db.commit()
            return notification

    async def create_notification(self, obj_in: NotificationCreate, override_user_id: Optional[int] = None) -> Notification:
        try:
            obj_data = obj_in.model_dump()
            user_id = override_user_id if override_user_id is not None else obj_data.get("user_id")
            user = None
            if not user_id:
                user_id = None
            elif user_id is not None:
                user = await self.db.get(User, user_id)
                if not user:
                    raise NotFoundError(f"User with id {user_id} not found")

            try:
                nt = NotificationType(obj_data["notification_type"])
            except ValueError:
                raise ValidationError(f"Invalid notification type: {obj_data['notification_type']}")

            try:
                nc = NotificationChannel(obj_data["channel"])
            except ValueError:
                raise ValidationError(f"Invalid notification channel: {obj_data['channel']}")

            priority_str = obj_data.get("priority", "normal")
            if priority_str == "medium":
                priority_str = "normal"
            try:
                np = NotificationPriority(priority_str)
            except ValueError:
                raise ValidationError(f"Invalid priority: {priority_str}")

            notification_code = await self._generate_notification_code(nt)

            # Auto-populate recipient email/phone from user when missing
            recipient_email = obj_data.get("recipient_email")
            recipient_phone = obj_data.get("recipient_phone")
            if not recipient_email and nc == NotificationChannel.EMAIL and user:
                recipient_email = user.email
            if not recipient_phone and nc == NotificationChannel.WHATSAPP and user:
                recipient_phone = user.phone_number

            notification = Notification(
                title=obj_data["title"],
                message=obj_data["message"],
                notification_code=notification_code,
                user_id=user_id,
                signal_id=obj_data.get("signal_id"),
                report_id=obj_data.get("report_id"),
                notification_type=nt,
                channel=nc,
                priority=np,
                status=NotificationStatus.PENDING,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                recipient_device_token=obj_data.get("recipient_device_token"),
                recipient_webhook_url=obj_data.get("recipient_webhook_url"),
                template_name=obj_data.get("template_name"),
                template_variables=obj_data.get("template_variables"),
                custom_data=obj_data.get("custom_data"),
                scheduled_at=obj_data.get("scheduled_at"),
                max_retries=obj_data.get("max_retries", 3),
                retry_delay_minutes=obj_data.get("retry_delay_minutes", 5),
                requires_action=obj_data.get("requires_action", False),
                action_url=obj_data.get("action_url"),
                action_button_text=obj_data.get("action_button_text"),
                expires_at=obj_data.get("expires_at")
            )

            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)

            await self.log_operation("create_notification", {"notification_id": notification.id, "code": notification_code})
            return notification
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            await self.log_error("create_notification", e)
            raise DatabaseError(f"Failed to create notification: {str(e)}")

    async def get_notification(self, notification_id: int) -> Notification:
        try:
            notification = await self.repository.get_notification_with_relations(notification_id=notification_id)
            if not notification:
                raise NotFoundError(f"Notification with id {notification_id} not found")
            return notification
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_notification", e, {"notification_id": notification_id})
            raise DatabaseError(f"Failed to get notification: {str(e)}")

    async def get_notifications(self, skip: int = 0, limit: int = 100,
                                 filters: Optional[Dict[str, Any]] = None) -> List[Notification]:
        try:
            if filters:
                return await self.repository.get_notifications_with_filters(
                    filters=filters, skip=skip, limit=limit
                )
            return await self.repository.get_multi(skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("get_notifications", e)
            raise DatabaseError(f"Failed to get notifications: {str(e)}")

    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Notification]:
        try:
            user = await self.db.get(User, user_id)
            if not user:
                raise NotFoundError(f"User with id {user_id} not found")
            return await self.repository.get_by_user(user_id=user_id, skip=skip, limit=limit)
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_user_notifications", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to get user notifications: {str(e)}")

    async def mark_as_read(self, notification_id: int, user_id: int) -> Notification:
        try:
            notification = await self.get_notification(notification_id)
            if notification.user_id and notification.user_id != user_id:
                raise AuthorizationError("Not authorized to mark this notification as read")
            await self.repository.mark_as_read(notification_id=notification_id)
            await self.db.refresh(notification)
            return notification
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            await self.log_error("mark_as_read", e, {"notification_id": notification_id})
            raise DatabaseError(f"Failed to mark notification as read: {str(e)}")

    async def mark_as_delivered(self, notification_id: int, receipt_data: Optional[dict] = None) -> Notification:
        try:
            notification = await self.get_notification(notification_id)
            notification.mark_as_delivered(receipt_data)
            await self.db.commit()
            await self.db.refresh(notification)
            return notification
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("mark_as_delivered", e, {"notification_id": notification_id})
            raise DatabaseError(f"Failed to mark notification as delivered: {str(e)}")

    async def mark_as_failed(self, notification_id: int, error_message: str) -> Notification:
        try:
            notification = await self.get_notification(notification_id)
            notification.mark_as_failed(error_message)
            await self.db.commit()
            await self.db.refresh(notification)
            return notification
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("mark_as_failed", e, {"notification_id": notification_id})
            raise DatabaseError(f"Failed to mark notification as failed: {str(e)}")

    async def send_notification(self, notification_id: int) -> Notification:
        try:
            notification = await self.get_notification(notification_id)

            if notification.status != NotificationStatus.PENDING:
                raise BusinessLogicError(
                    f"Cannot send notification in status '{notification.status.value}'. Must be PENDING."
                )

            notification = await self._render_template(notification)
            notification = await self._deliver_via_channel(notification)

            await self.log_operation("send_notification", {"notification_id": notification_id})
            return notification
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("send_notification", e, {"notification_id": notification_id})
            raise DatabaseError(f"Failed to send notification: {str(e)}")

    async def send_bulk_notifications(self, notification_ids: List[int]) -> List[Notification]:
        results = []
        for nid in notification_ids:
            try:
                result = await self.send_notification(nid)
                results.append(result)
            except Exception as e:
                logger.error("Bulk notification failed", notification_id=nid, error=str(e))
                try:
                    await self.mark_as_failed(nid, str(e))
                except Exception:
                    pass
        return results

    async def send_signal_notification(self, signal_id: int, notification_type: NotificationType,
                                        channel: NotificationChannel = NotificationChannel.IN_APP,
                                        custom_message: Optional[str] = None) -> Notification:
        try:
            from app.models.signal import Signal
            signal_query = select(Signal).where(Signal.id == signal_id)
            signal_result = await self.db.execute(signal_query)
            signal = signal_result.scalar_one_or_none()
            if not signal:
                raise NotFoundError(f"Signal with id {signal_id} not found")

            user_query = select(User).where(User.id == signal.created_by)
            user_result = await self.db.execute(user_query)
            user = user_result.scalar_one_or_none()

            if not user:
                raise NotFoundError(f"User {signal.created_by} not found for notification")

            type_titles = {
                NotificationType.SIGNAL_CREATED: "Signal Created",
                NotificationType.SIGNAL_ASSIGNED: "Signal Assigned",
                NotificationType.SIGNAL_UPDATED: "Signal Updated",
                NotificationType.SIGNAL_RESOLVED: "Signal Resolved",
                NotificationType.SIGNAL_ESCALATED: "Signal Escalated"
            }

            title = type_titles.get(notification_type, f"Signal {signal.reference_number}")

            message = custom_message or (
                f"Your signal '{signal.title}' ({signal.reference_number}) "
                f"has been {notification_type.value.replace('signal_', '')}"
            )

            notif_in = NotificationCreate(
                title=title,
                message=message,
                notification_type=notification_type.value,
                channel=channel.value,
                user_id=user.id,
                signal_id=signal_id,
                priority="high" if notification_type in [
                    NotificationType.SIGNAL_ESCALATED, NotificationType.SIGNAL_ASSIGNED
                ] else "normal"
            )

            notification = await self.create_notification(notif_in)
            return await self.send_notification(notification.id)
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("send_signal_notification", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to send signal notification: {str(e)}")

    async def get_notification_stats(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            stats = await self.repository.get_notification_statistics(filters=filters)

            total = stats.get("total_notifications", 0)
            by_status = stats.get("notifications_by_status", {})
            sent = by_status.get("sent", 0) or 0
            delivered = by_status.get("delivered", 0) or 0
            failed = by_status.get("failed", 0) or 0
            read_count = by_status.get("read", 0) or 0

            processed = sent + delivered + failed + read_count
            success_rate = round((sent + delivered + read_count) / processed * 100, 2) if processed > 0 else 0

            stats["success_rate"] = success_rate
            stats["total_processed"] = processed
            return stats
        except Exception as e:
            await self.log_error("get_notification_stats", e)
            raise DatabaseError(f"Failed to get notification stats: {str(e)}")

    async def retry_failed(self, notification_id: int) -> Notification:
        try:
            notification = await self.get_notification(notification_id)

            if not notification.can_retry:
                raise BusinessLogicError(
                    f"Notification cannot be retried. "
                    f"Retries: {notification.retry_count}/{notification.max_retries}, "
                    f"Expired: {notification.is_expired}"
                )

            notification.status = NotificationStatus.PENDING
            notification.error_message = None
            notification.error_code = None
            notification.failed_at = None
            await self.db.commit()

            notification = await self.send_notification(notification_id)
            return notification
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("retry_failed", e, {"notification_id": notification_id})
            raise DatabaseError(f"Failed to retry notification: {str(e)}")

    async def cancel_notification(self, notification_id: int) -> Notification:
        try:
            notification = await self.get_notification(notification_id)

            if notification.status in [NotificationStatus.READ, NotificationStatus.DELIVERED]:
                raise BusinessLogicError(
                    f"Cannot cancel notification in status '{notification.status.value}'"
                )

            if notification.status == NotificationStatus.CANCELLED:
                raise BusinessLogicError("Notification is already cancelled")

            notification.status = NotificationStatus.CANCELLED
            await self.db.commit()
            await self.db.refresh(notification)

            await self.log_operation("cancel_notification", {"notification_id": notification_id})
            return notification
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("cancel_notification", e, {"notification_id": notification_id})
            raise DatabaseError(f"Failed to cancel notification: {str(e)}")

    async def _get_users_by_recipient_type(self, recipient_type: str, sector_id: Optional[int] = None) -> List:
        from app.models.user import User, UserRole

        query = select(User)

        if recipient_type == "all_citizens":
            query = query.where(User.role == UserRole.CITIZEN)
        elif recipient_type == "all_admins":
            query = query.where(User.role == UserRole.ADMIN)
        elif recipient_type == "all_sector_users":
            query = query.where(User.role == UserRole.SECTOR)
            if sector_id:
                query = query.where(User.sector_id == sector_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def send_bulk_to_group(self, obj_in) -> Dict[str, Any]:
        users = await self._get_users_by_recipient_type(
            obj_in.recipient_type, obj_in.sector_id
        )
        if not users:
            raise NotFoundError(
                f"No active users found for recipient_type '{obj_in.recipient_type}'"
            )

        total_created = 0
        total_sent = 0
        errors = []

        for user in users:
            try:
                notification = await self.create_notification(obj_in, override_user_id=user.id)
                await self.send_notification(notification.id)
                total_created += 1
                total_sent += 1
            except Exception as e:
                errors.append({"user_id": user.id, "error": str(e)})

        return {
            "recipient_type": obj_in.recipient_type,
            "total_users": len(users),
            "notifications_created": total_created,
            "notifications_sent": total_sent,
            "errors": errors,
        }

    async def cleanup_expired(self, days: int = 30) -> Dict[str, int]:
        try:
            deleted = await self.repository.cleanup_old_notifications(days=days)

            expired_query = select(Notification).where(
                and_(
                    Notification.expires_at < datetime.now(timezone.utc),
                    Notification.status.in_([
                        NotificationStatus.PENDING,
                        NotificationStatus.SENT
                    ])
                )
            )
            expired_result = await self.db.execute(expired_query)
            expired = expired_result.scalars().all()

            cancelled_count = 0
            for notif in expired:
                notif.status = NotificationStatus.CANCELLED
                cancelled_count += 1

            if cancelled_count > 0:
                await self.db.commit()

            await self.log_operation("cleanup_expired", {
                "deleted": deleted, "cancelled": cancelled_count, "days": days
            })
            return {"deleted": deleted, "cancelled": cancelled_count}
        except Exception as e:
            await self.log_error("cleanup_expired", e)
            raise DatabaseError(f"Failed to cleanup expired notifications: {str(e)}")
