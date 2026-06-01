"""
WhatsApp Service - Urbain Sustainability System
Uses pywhatkit (WhatsApp Web automation) as default — free, no API keys needed.
Falls back to mock/log mode if WhatsApp Web is unavailable.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

import structlog

from app.core.exceptions import (
    ExternalServiceError,
    ValidationError,
    ServiceUnavailableError
)
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.services.base import BaseService
from app.utils.validators import validate_phone

logger = structlog.get_logger()


class WhatsAppService(BaseService):

    def __init__(self, db):
        super().__init__(db)

    async def _send_via_pywhatkit(self, to: str, message: str) -> Dict[str, Any]:
        try:
            import pywhatkit
            loop = asyncio.get_event_loop()

            def _send():
                pywhatkit.sendwhatmsg_instantly(
                    to, message,
                    wait_time=20,
                    tab_close=True,
                    close_time=3
                )
                return {"success": True, "message_id": str(uuid.uuid4())}

            result = await loop.run_in_executor(None, _send)
            logger.info("WhatsApp sent via pywhatkit", to=to)
            return {
                "success": True,
                "provider": "pywhatkit",
                "provider_message_id": result.get("message_id", str(uuid.uuid4())),
            }
        except ImportError:
            logger.warning("pywhatkit not installed - falling back to mock")
            return await self._send_mock(to, message)
        except Exception as e:
            logger.warning("pywhatkit send error", error=str(e))
            return await self._send_mock(to, message)

    async def _send_mock(self, to: str, message: str) -> Dict[str, Any]:
        logger.info("Mock WhatsApp message", to=to, message=message)
        return {
            "success": True,
            "provider": "mock",
            "provider_message_id": str(uuid.uuid4()),
            "simulated": True
        }

    async def _log_whatsapp_notification(
        self,
        phone: str,
        message: str,
        notification_type: str,
        provider_message_id: Optional[str] = None,
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Optional[int]:
        try:
            notification_code = f"WA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{phone[-4:]}"
            notification = Notification(
                title=f"WhatsApp Notification - {notification_type}",
                message=message,
                notification_code=notification_code,
                notification_type=NotificationType[notification_type.upper()] if notification_type.upper() in NotificationType.__members__ else NotificationType.SYSTEM_ALERT,
                channel=NotificationChannel.WHATSAPP,
                status=NotificationStatus.SENT,
                recipient_phone=phone,
                user_id=user_id,
                signal_id=signal_id,
                external_id=provider_message_id
            )
            self.db.add(notification)
            await self.db.commit()
            return notification.id
        except Exception as e:
            logger.warning("Failed to log WhatsApp notification", error=str(e))
            return None

    async def send_whatsapp(
        self,
        to_phone: str,
        message: str,
        notification_type: str = "SYSTEM_ALERT",
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            validated_phone = validate_phone(to_phone)
            cleaned = validated_phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not cleaned.startswith("+"):
                cleaned = "+216" + cleaned.lstrip("0")
            formatted_phone = cleaned

            if not message or len(message.strip()) == 0:
                raise ValidationError("Message cannot be empty")

            if len(message) > 1600:
                raise ValidationError("Message exceeds maximum length of 1600 characters")

            provider_result = await self._send_via_pywhatkit(formatted_phone, message)

            notification_id = await self._log_whatsapp_notification(
                phone=formatted_phone,
                message=message,
                notification_type=notification_type,
                provider_message_id=provider_result.get("provider_message_id"),
                user_id=user_id,
                signal_id=signal_id
            )

            result = {
                "success": provider_result["success"],
                "recipient": formatted_phone,
                "message_length": len(message),
                "notification_id": notification_id,
                "provider": provider_result.get("provider"),
                "provider_message_id": provider_result.get("provider_message_id"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await self.log_operation("send_whatsapp", {
                "recipient": formatted_phone,
                "provider": provider_result.get("provider"),
                "notification_id": notification_id
            })

            return result

        except (ValidationError, ExternalServiceError):
            raise
        except Exception as e:
            await self.log_error("send_whatsapp", e)
            raise ExternalServiceError("Failed to send WhatsApp message")

    async def send_alert(
        self,
        to_phone: str,
        alert_title: str,
        alert_message: str,
        priority: str = "normal",
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            validated_phone = validate_phone(to_phone)

            prefix = ""
            if priority == "critical":
                prefix = "🚨 CRITICAL ALERT 🚨\n\n"
            elif priority == "high":
                prefix = "⚠️ URGENT ⚠️\n\n"

            message = f"{prefix}{alert_title}\n\n{alert_message[:1400]}"

            result = await self.send_whatsapp(
                to_phone=validated_phone,
                message=message,
                notification_type="SYSTEM_ALERT",
                user_id=user_id,
                signal_id=signal_id
            )

            result["alert_priority"] = priority

            await self.log_operation("send_alert", {
                "phone": validated_phone,
                "priority": priority,
                "title": alert_title
            })

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_alert", e)
            raise ExternalServiceError("Failed to send WhatsApp alert")

    async def send_bulk(
        self,
        recipients: List[str],
        message: str,
        batch_size: int = 10
    ) -> Dict[str, Any]:
        try:
            if not recipients:
                raise ValidationError("No recipients provided")

            if len(recipients) > 1000:
                raise ValidationError("Maximum 1000 recipients allowed")

            results = {
                "total": len(recipients),
                "successful": 0,
                "failed": 0,
                "errors": []
            }

            for i in range(0, len(recipients), batch_size):
                batch = recipients[i:i + batch_size]
                for recipient in batch:
                    try:
                        await self.send_whatsapp(to_phone=recipient, message=message)
                        results["successful"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "recipient": recipient,
                            "error": str(e)
                        })

                if i + batch_size < len(recipients):
                    await asyncio.sleep(1)

            await self.log_operation("send_bulk_whatsapp", {
                "total": results["total"],
                "successful": results["successful"],
                "failed": results["failed"]
            })

            return results

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_bulk_whatsapp", e)
            raise ExternalServiceError("Failed to send bulk WhatsApp messages")
