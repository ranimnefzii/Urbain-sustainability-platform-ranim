"""
Notification Routes - Urbain Sustainability System
Routes de gestion des notifications et alertes
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.schemas.notification import NotificationCreate, NotificationSend, NotificationUpdate
from app.services.notification_service import NotificationService
from app.core.exceptions import (
    NotFoundError, ValidationError, DatabaseError, BusinessLogicError, AuthorizationError
)
from app.utils.helpers import Paginator

logger = structlog.get_logger()
router = APIRouter()


def _serialize_notification(n):
    return {c.name: getattr(n, c.name) for c in n.__table__.columns}


@router.get("/", response_model=dict, summary="List user notifications",
             description="Get paginated notifications for the current user")
async def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    notification_type: Optional[str] = Query(None, description="Filter by type"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        service = NotificationService(db)
        filters = {"user_id": current_user.id}
        if notification_type:
            filters["notification_type"] = notification_type
        if channel:
            filters["channel"] = channel
        if status:
            filters["status"] = status
        notifications = await service.get_notifications(paginator.skip, paginator.size, filters)
        total = len(notifications)
        serialized = [_serialize_notification(n) for n in notifications]
        return {
            "success": True,
            "message": "Notifications retrieved",
            "data": {
                "items": serialized,
                **paginator.get_metadata(total)
            }
        }
    except Exception as e:
        logger.error("List notifications failed", error=str(e))
        raise DatabaseError("Failed to retrieve notifications")


@router.get("/stats", response_model=dict, summary="Get notification stats",
             description="Get statistics about user's notifications")
async def get_notification_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        stats = await service.get_notification_stats(filters={"user_id": current_user.id})
        return {"success": True, "message": "Notification stats retrieved", "data": stats}
    except Exception as e:
        logger.error("Get notification stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve notification stats")


@router.put("/{notification_id}/read", response_model=dict, summary="Mark notification as read",
             description="Mark a notification as read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        notification = await service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user.id
        )
        return {"success": True, "message": "Notification marked as read", "data": _serialize_notification(notification)}
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error("Mark notification read failed", error=str(e))
        raise DatabaseError("Failed to mark notification as read")


@router.put("/read-all", response_model=dict, summary="Mark all notifications as read",
             description="Mark all user's notifications as read")
async def mark_all_notifications_read(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        notifications = await service.get_notifications(0, 1000, {"user_id": current_user.id})
        count = 0
        for notif in notifications:
            if notif.status.value == "read":
                continue
            try:
                await service.mark_as_read(notif.id, current_user.id)
                count += 1
            except Exception:
                continue
        return {"success": True, "message": f"{count} notifications marked as read", "data": {"marked_read": count}}
    except Exception as e:
        logger.error("Mark all notifications read failed", error=str(e))
        raise DatabaseError("Failed to mark all notifications as read")


@router.post("/send", response_model=dict, summary="Send a notification",
              description="Create and immediately send a notification (supports single user or bulk group)")
async def send_notification(
    data: NotificationSend,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)

        # Bulk send to a group
        if data.recipient_type:
            if data.recipient_type in ("all_citizens", "all_admins", "all_sector_users"):
                result = await service.send_bulk_to_group(data)
                return {
                    "success": True,
                    "message": f"Notification sent to {result['notifications_sent']} of {result['total_users']} users",
                    "data": result
                }
            elif data.recipient_type == "custom_email" and data.recipient_email:
                notification = await service.create_notification(data)
                result = await service.send_notification(notification.id)
                return {"success": True, "message": "Notification sent", "data": _serialize_notification(result)}
            elif data.recipient_type == "custom_phone" and data.recipient_phone:
                notification = await service.create_notification(data)
                result = await service.send_notification(notification.id)
                return {"success": True, "message": "Notification sent", "data": _serialize_notification(result)}
            else:
                raise ValidationError(f"Invalid recipient configuration for type '{data.recipient_type}'")

        # Single user send
        notification = await service.create_notification(data)
        result = await service.send_notification(notification.id)
        return {"success": True, "message": "Notification sent", "data": _serialize_notification(result)}
    except (BusinessLogicError, NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error("Send notification failed", error=str(e), exc_info=True)
        raise DatabaseError(f"Failed to send notification: {str(e)}")


@router.post("/{notification_id}/retry", response_model=dict, summary="Retry failed notification",
              description="Reset a failed notification to PENDING and retry sending")
async def retry_notification(
    notification_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        result = await service.retry_failed(notification_id)
        return {"success": True, "message": "Retry initiated", "data": _serialize_notification(result)}
    except (NotFoundError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error("Retry notification failed", error=str(e))
        raise DatabaseError("Failed to retry notification")


@router.post("/{notification_id}/cancel", response_model=dict, summary="Cancel a notification",
              description="Cancel a pending or sent notification")
async def cancel_notification(
    notification_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        result = await service.cancel_notification(notification_id)
        return {"success": True, "message": "Notification cancelled", "data": _serialize_notification(result)}
    except (NotFoundError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error("Cancel notification failed", error=str(e))
        raise DatabaseError("Failed to cancel notification")


@router.post("/cleanup-expired", response_model=dict, summary="Cleanup expired notifications",
              description="Delete/expire old notifications past their expiration date")
async def cleanup_expired_notifications(
    days: int = Query(30, ge=1, le=365, description="Delete notifications older than N days"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        result = await service.cleanup_expired(days=days)
        return {"success": True, "message": "Expired notifications cleaned up", "data": result}
    except Exception as e:
        logger.error("Cleanup notifications failed", error=str(e))
        raise DatabaseError("Failed to cleanup notifications")


@router.post("/retry-all-failed", response_model=dict, summary="Retry all failed notifications",
              description="Retry all notifications in FAILED status")
async def retry_all_failed(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        failed = await service.get_notifications(0, 1000, {"status": "failed"})
        results = await service.send_bulk_notifications([n.id for n in failed])
        return {"success": True, "message": f"Retried {len(results)} failed notifications", "data": {"retried": len(results), "total_failed": len(failed)}}
    except Exception as e:
        logger.error("Retry all failed failed", error=str(e))
        raise DatabaseError("Failed to retry all notifications")
