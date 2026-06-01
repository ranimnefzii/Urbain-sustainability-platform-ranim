"""
Push Service - Urbain Sustainability System
Service de notifications push pour applications mobiles et web
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

import structlog

from app.core.exceptions import (
    ExternalServiceError,
    ValidationError,
    NotFoundError,
    ServiceUnavailableError
)
from app.core.config import settings
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.services.base import BaseService

logger = structlog.get_logger()


class PushService(BaseService):
    """
    Service de notifications push pour applications mobiles (Firebase/APNs) et web
    Gère l'enregistrement des devices et l'envoi de notifications push
    """

    PLATFORM_FCM = "fcm"
    PLATFORM_APNS = "apns"
    PLATFORM_WEB = "web_push"
    PLATFORM_UNKNOWN = "unknown"

    def __init__(self, db):
        super().__init__(db)
        self.notification_repo = NotificationRepository(db, Notification)
        self._device_tokens: Dict[int, List[Dict[str, Any]]] = {}

    async def _send_fcm(self, token: str, title: str, body: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging

            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                token=token
            )
            response = messaging.send(message)
            return {
                "success": True,
                "platform": self.PLATFORM_FCM,
                "message_id": response
            }
        except ImportError:
            logger.warning("Firebase SDK not installed - simulating push")
            return await self._send_mock_push(token, title, body, data, self.PLATFORM_FCM)
        except Exception as e:
            logger.error("FCM send error", error=str(e))
            raise ServiceUnavailableError("Firebase Cloud Messaging unavailable")

    async def _send_apns(self, token: str, title: str, body: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            from apns2.client import APNsClient
            from apns2.payload import Payload

            client = APNsClient(
                settings.APNS_KEY_PATH,
                use_sandbox=settings.ENVIRONMENT != "production"
            )
            payload = Payload(alert={"title": title, "body": body}, badge=1, sound="default")
            client.send_notification(token, payload)
            return {
                "success": True,
                "platform": self.PLATFORM_APNS,
                "message_id": str(uuid.uuid4())
            }
        except ImportError:
            logger.warning("APNs SDK not installed - simulating push")
            return await self._send_mock_push(token, title, body, data, self.PLATFORM_APNS)
        except Exception as e:
            logger.error("APNs send error", error=str(e))
            raise ServiceUnavailableError("Apple Push Notification service unavailable")

    async def _send_web_push(self, token: str, title: str, body: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            from pywebpush import webpush, WebPushException

            token_data = json.loads(token)
            response = webpush(
                subscription_info=token_data,
                data=json.dumps({
                    "title": title,
                    "body": body,
                    "data": data or {}
                }),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIM_EMAIL}"}
            )
            return {
                "success": True,
                "platform": self.PLATFORM_WEB,
                "message_id": str(uuid.uuid4())
            }
        except ImportError:
            logger.warning("Web Push SDK not installed - simulating push")
            return await self._send_mock_push(token, title, body, data, self.PLATFORM_WEB)
        except Exception as e:
            logger.error("Web Push send error", error=str(e))
            raise ServiceUnavailableError("Web Push service unavailable")

    async def _send_mock_push(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        platform: str = "mock"
    ) -> Dict[str, Any]:
        logger.info("Mock push notification", platform=platform, token=token[:20], title=title)
        return {
            "success": True,
            "platform": platform,
            "message_id": str(uuid.uuid4()),
            "simulated": True
        }

    async def _detect_platform(self, token: str) -> str:
        if token.startswith("fcm-") or token.startswith("c-"):
            return self.PLATFORM_FCM
        if token.startswith("apns-") or len(token) > 100 and "." in token:
            return self.PLATFORM_APNS
        if token.startswith("{") and token.endswith("}"):
            return self.PLATFORM_WEB
        return self.PLATFORM_FCM

    async def _send_to_platform(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        if not platform:
            platform = await self._detect_platform(token)

        if platform == self.PLATFORM_FCM:
            return await self._send_fcm(token, title, body, data)
        elif platform == self.PLATFORM_APNS:
            return await self._send_apns(token, title, body, data)
        elif platform == self.PLATFORM_WEB:
            return await self._send_web_push(token, title, body, data)
        else:
            return await self._send_mock_push(token, title, body, data, platform)

    async def _log_push_notification(
        self,
        token: str,
        title: str,
        body: str,
        platform: str,
        notification_type: str,
        provider_message_id: Optional[str] = None,
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Optional[int]:
        try:
            notification_code = f"PUSH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{token[-8:]}"
            notification = Notification(
                title=title,
                message=body,
                notification_code=notification_code,
                notification_type=NotificationType[notification_type.upper()] if notification_type.upper() in NotificationType.__members__ else NotificationType.SYSTEM_ALERT,
                channel=NotificationChannel.PUSH,
                status=NotificationStatus.SENT,
                recipient_device_token=token,
                user_id=user_id,
                signal_id=signal_id,
                external_id=provider_message_id,
                push_config={"platform": platform}
            )
            self.db.add(notification)
            await self.db.commit()
            return notification.id
        except Exception as e:
            logger.warning("Failed to log push notification", error=str(e))
            return None

    async def send_push(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        platform: Optional[str] = None,
        notification_type: str = "SYSTEM_ALERT",
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            if not token:
                raise ValidationError("Device token is required")
            if not title or len(title.strip()) == 0:
                raise ValidationError("Title cannot be empty")
            if not body or len(body.strip()) == 0:
                raise ValidationError("Body cannot be empty")

            detected_platform = platform or await self._detect_platform(token)
            provider_result = await self._send_to_platform(token, title, body, data, detected_platform)

            notification_id = await self._log_push_notification(
                token=token,
                title=title,
                body=body,
                platform=detected_platform,
                notification_type=notification_type,
                provider_message_id=provider_result.get("message_id"),
                user_id=user_id,
                signal_id=signal_id
            )

            result = {
                "success": provider_result["success"],
                "platform": detected_platform,
                "notification_id": notification_id,
                "provider_message_id": provider_result.get("message_id"),
                "simulated": provider_result.get("simulated", False),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await self.log_operation("send_push", {
                "platform": detected_platform,
                "title": title,
                "notification_id": notification_id
            })

            return result

        except (ValidationError, ExternalServiceError):
            raise
        except Exception as e:
            await self.log_error("send_push", e)
            raise ExternalServiceError("Failed to send push notification")

    async def send_signal_push(
        self,
        token: str,
        signal_ref: str,
        signal_title: str,
        status: str,
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            title = f"Signal {signal_ref} Updated"
            body = f"{signal_title[:150]} - Status: {status}"
            data = {
                "type": "signal_update",
                "reference_number": signal_ref,
                "signal_id": str(signal_id) if signal_id else "",
                "status": status
            }

            return await self.send_push(
                token=token,
                title=title,
                body=body,
                data=data,
                notification_type="SIGNAL_UPDATED",
                user_id=user_id,
                signal_id=signal_id
            )

        except Exception as e:
            await self.log_error("send_signal_push", e)
            raise ExternalServiceError("Failed to send signal push notification")

    async def send_alert_push(
        self,
        token: str,
        alert_title: str,
        alert_body: str,
        priority: str = "normal",
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            push_title = alert_title
            if priority == "critical":
                push_title = "🚨 " + alert_title
            elif priority == "high":
                push_title = "⚠️ " + alert_title

            data = {
                "type": "alert",
                "priority": priority,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            return await self.send_push(
                token=token,
                title=push_title,
                body=alert_body[:200],
                data=data,
                notification_type="SYSTEM_ALERT",
                user_id=user_id,
                signal_id=signal_id
            )

        except Exception as e:
            await self.log_error("send_alert_push", e)
            raise ExternalServiceError("Failed to send alert push notification")

    async def send_bulk_push(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        try:
            if not tokens:
                raise ValidationError("No device tokens provided")

            if len(tokens) > 10000:
                raise ValidationError("Maximum 10000 tokens allowed")

            results = {
                "total": len(tokens),
                "successful": 0,
                "failed": 0,
                "errors": []
            }

            for i in range(0, len(tokens), batch_size):
                batch = tokens[i:i + batch_size]
                for token in batch:
                    try:
                        await self.send_push(
                            token=token,
                            title=title,
                            body=body,
                            data=data
                        )
                        results["successful"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "token": token[:20] + "...",
                            "error": str(e)
                        })

                if i + batch_size < len(tokens):
                    import asyncio
                    await asyncio.sleep(0.1)

            await self.log_operation("send_bulk_push", {
                "total": results["total"],
                "successful": results["successful"],
                "failed": results["failed"]
            })

            return results

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_bulk_push", e)
            raise ExternalServiceError("Failed to send bulk push notifications")

    async def register_device(
        self,
        user_id: int,
        device_token: str,
        platform: str = "fcm",
        device_name: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            if not device_token:
                raise ValidationError("Device token is required")

            valid_platforms = [self.PLATFORM_FCM, self.PLATFORM_APNS, self.PLATFORM_WEB]
            if platform not in valid_platforms:
                raise ValidationError(f"Invalid platform. Must be one of: {valid_platforms}")

            if user_id not in self._device_tokens:
                self._device_tokens[user_id] = []

            existing = [
                d for d in self._device_tokens[user_id]
                if d["token"] == device_token
            ]
            if existing:
                existing[0]["platform"] = platform
                existing[0]["device_name"] = device_name
                existing[0]["device_info"] = device_info or {}
                existing[0]["updated_at"] = datetime.now(timezone.utc).isoformat()
                return {
                    "success": True,
                    "message": "Device token updated",
                    "device_token": device_token,
                    "platform": platform,
                    "registered": False
                }

            self._device_tokens[user_id].append({
                "token": device_token,
                "platform": platform,
                "device_name": device_name or "Unknown Device",
                "device_info": device_info or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_active": True
            })

            await self.audit_log(
                action="device_registered",
                entity_type="device",
                entity_id=user_id,
                user_id=user_id,
                new_values={"platform": platform, "device_token": device_token[:20]}
            )

            await self.log_operation("register_device", {
                "user_id": user_id,
                "platform": platform,
                "device_name": device_name
            })

            return {
                "success": True,
                "message": "Device registered successfully",
                "device_token": device_token,
                "platform": platform,
                "registered": True
            }

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("register_device", e)
            raise ExternalServiceError("Failed to register device")

    async def unregister_device(
        self,
        user_id: int,
        device_token: str
    ) -> Dict[str, str]:
        try:
            if not device_token:
                raise ValidationError("Device token is required")

            if user_id in self._device_tokens:
                self._device_tokens[user_id] = [
                    d for d in self._device_tokens[user_id]
                    if d["token"] != device_token
                ]

            await self.audit_log(
                action="device_unregistered",
                entity_type="device",
                entity_id=user_id,
                user_id=user_id,
                old_values={"device_token": device_token[:20]}
            )

            await self.log_operation("unregister_device", {
                "user_id": user_id,
                "token_preview": device_token[:20]
            })

            return {"message": "Device unregistered successfully"}

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("unregister_device", e)
            raise ExternalServiceError("Failed to unregister device")

    async def get_user_devices(self, user_id: int) -> List[Dict[str, Any]]:
        devices = self._device_tokens.get(user_id, [])
        return [
            {
                "token": d["token"][:20] + "...",
                "platform": d["platform"],
                "device_name": d.get("device_name"),
                "is_active": d.get("is_active", True),
                "created_at": d.get("created_at"),
                "updated_at": d.get("updated_at")
            }
            for d in devices
        ]
