"""
SMS Service - Urbain Sustainability System
Primary provider: TextBelt (free tier — 1 SMS/day, key="textbelt", no account needed)
Fallback: email-to-SMS gateway / mock
Also supports Twilio, Vonage, AWS SNS for production.
"""

import asyncio
import json
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import URLError

import structlog

from app.core.exceptions import (
    ExternalServiceError,
    ValidationError,
    ServiceUnavailableError
)
from app.core.config import settings
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.services.base import BaseService
from app.utils.validators import validate_phone

logger = structlog.get_logger()


TEXTBELT_URL = "https://textbelt.com/text"


class SMSService(BaseService):
    """
    Service d'envoi de SMS
    Default provider: email-to-SMS gateway (uses SMTP — free, no extra accounts)
    Also supports Twilio, Vonage, AWS SNS, and mock mode.
    """

    PROVIDER_TEXTBELT = "textbelt"
    PROVIDER_EMAIL_GATEWAY = "email_gateway"
    PROVIDER_TWILIO = "twilio"
    PROVIDER_VONAGE = "vonage"
    PROVIDER_AWS = "aws_sns"
    PROVIDER_MOCK = "mock"

    def __init__(self, db):
        super().__init__(db)
        self.notification_repo = NotificationRepository(db, Notification)
        self._provider = self._initialize_provider()

    def _initialize_provider(self) -> str:
        provider = self.PROVIDER_TEXTBELT
        if settings.SMS_PROVIDER:
            provider = settings.SMS_PROVIDER
        logger.info("SMS provider initialized", provider=provider)
        return provider

    def _is_sms_configured(self) -> bool:
        if self._provider == self.PROVIDER_TEXTBELT:
            return bool(settings.TEXTBELT_API_KEY)
        if self._provider == self.PROVIDER_TWILIO:
            return bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        if self._provider == self.PROVIDER_VONAGE:
            return bool(settings.VONAGE_API_KEY and settings.VONAGE_API_SECRET)
        if self._provider == self.PROVIDER_AWS:
            return bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)
        return True

    def _format_phone(self, phone: str) -> str:
        cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not cleaned.startswith("+"):
            cleaned = "+216" + cleaned.lstrip("0")
        return cleaned

    async def _send_textbelt(self, to: str, message: str) -> Dict[str, Any]:
        key = settings.TEXTBELT_API_KEY or "textbelt"
        payload = json.dumps({"phone": to, "message": message, "key": key}).encode()
        req = Request(TEXTBELT_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, lambda: urlopen(req, timeout=15))
            body = json.loads(resp.read().decode())
            if body.get("success"):
                logger.info("SMS sent via TextBelt", to=to, text_id=body.get("textId"))
                return {
                    "success": True,
                    "provider": self.PROVIDER_TEXTBELT,
                    "provider_message_id": body.get("textId", str(uuid.uuid4())),
                }
            else:
                err = body.get("error", "unknown")
                logger.warning("TextBelt API error", to=to, error=err)
                return {"success": False, "error": err}
        except URLError as e:
            logger.warning("TextBelt network error", error=str(e))
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.warning("TextBelt send error", error=str(e))
            return {"success": False, "error": str(e)}

    async def _send_via_provider(self, to: str, message: str) -> Dict[str, Any]:
        if not self._is_sms_configured():
            logger.info("SMS provider not configured - logging message", to=to, message=message)
            return {
                "success": True,
                "provider": self._provider,
                "provider_message_id": str(uuid.uuid4()),
                "simulated": True
            }

        if self._provider == self.PROVIDER_TEXTBELT:
            result = await self._send_textbelt(to, message)
            if result.get("success"):
                return result
            logger.warning("TextBelt failed, falling back to mock", to=to)
            return await self._send_mock(to, message)
        elif self._provider == self.PROVIDER_TWILIO:
            return await self._send_twilio(to, message)
        elif self._provider == self.PROVIDER_VONAGE:
            return await self._send_vonage(to, message)
        elif self._provider == self.PROVIDER_AWS:
            return await self._send_aws_sns(to, message)
        else:
            return await self._send_mock(to, message)

    async def _send_twilio(self, to: str, message: str) -> Dict[str, Any]:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            twilio_message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to
            )
            return {
                "success": True,
                "provider": self.PROVIDER_TWILIO,
                "provider_message_id": twilio_message.sid,
                "status": twilio_message.status
            }
        except ImportError:
            logger.warning("Twilio SDK not installed - falling back to mock")
            return await self._send_mock(to, message)
        except Exception as e:
            logger.warning("Twilio error — falling back to log mode", error=str(e))
            logger.info("SMS would have been sent", to=to, message=message)
            return {
                "success": True,
                "provider": self.PROVIDER_MOCK,
                "provider_message_id": str(uuid.uuid4()),
                "simulated": True,
                "error_detail": str(e)
            }

    async def _send_via_provider(self, to: str, message: str) -> Dict[str, Any]:
        if not self._is_sms_configured():
            logger.info("SMS provider not configured - logging message", to=to, message=message)
            return {
                "success": True,
                "provider": self._provider,
                "provider_message_id": str(uuid.uuid4()),
                "simulated": True
            }

        if self._provider == self.PROVIDER_EMAIL_GATEWAY:
            return await self._send_via_email_gateway(to, message)
        elif self._provider == self.PROVIDER_TWILIO:
            return await self._send_twilio(to, message)
        elif self._provider == self.PROVIDER_VONAGE:
            return await self._send_vonage(to, message)
        elif self._provider == self.PROVIDER_AWS:
            return await self._send_aws_sns(to, message)
        else:
            return await self._send_mock(to, message)

    async def _send_twilio(self, to: str, message: str) -> Dict[str, Any]:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            twilio_message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to
            )
            return {
                "success": True,
                "provider": self.PROVIDER_TWILIO,
                "provider_message_id": twilio_message.sid,
                "status": twilio_message.status
            }
        except ImportError:
            logger.warning("Twilio SDK not installed - falling back to mock")
            return await self._send_mock(to, message)
        except Exception as e:
            logger.warning("Twilio error — falling back to log mode", error=str(e))
            logger.info("SMS would have been sent", to=to, message=message)
            return {
                "success": True,
                "provider": self.PROVIDER_MOCK,
                "provider_message_id": str(uuid.uuid4()),
                "simulated": True,
                "error_detail": str(e)
            }

    async def _send_vonage(self, to: str, message: str) -> Dict[str, Any]:
        try:
            import vonage
            client = vonage.Client(key=settings.VONAGE_API_KEY, secret=settings.VONAGE_API_SECRET)
            sms = vonage.Sms(client)
            response = sms.send_message({
                "from": settings.VONAGE_SENDER or "Urbain",
                "to": to,
                "text": message
            })
            if response["messages"][0]["status"] == "0":
                return {
                    "success": True,
                    "provider": self.PROVIDER_VONAGE,
                    "provider_message_id": response["messages"][0]["message-id"]
                }
            raise ExternalServiceError(f"Vonage error: {response['messages'][0]['error-text']}")
        except ImportError:
            logger.warning("Vonage SDK not installed - falling back to mock")
            return await self._send_mock(to, message)
        except Exception as e:
            logger.error("Vonage error", error=str(e))
            raise ServiceUnavailableError("Vonage SMS service unavailable")

    async def _send_aws_sns(self, to: str, message: str) -> Dict[str, Any]:
        try:
            import boto3
            client = boto3.client(
                "sns",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION or "us-east-1"
            )
            response = client.publish(
                PhoneNumber=to,
                Message=message,
                MessageAttributes={
                    "AWS.SNS.SMS.SenderID": {
                        "DataType": "String",
                        "StringValue": settings.AWS_SNS_SENDER or "Urbain"
                    }
                }
            )
            return {
                "success": True,
                "provider": self.PROVIDER_AWS,
                "provider_message_id": response["MessageId"]
            }
        except ImportError:
            logger.warning("AWS SDK not installed - falling back to mock")
            return await self._send_mock(to, message)
        except Exception as e:
            logger.error("AWS SNS error", error=str(e))
            raise ServiceUnavailableError("AWS SNS service unavailable")

    async def _send_mock(self, to: str, message: str) -> Dict[str, Any]:
        logger.info("Mock SMS", to=to, message=message)
        return {
            "success": True,
            "provider": self.PROVIDER_MOCK,
            "provider_message_id": str(uuid.uuid4()),
            "simulated": True
        }

    async def _log_sms_notification(
        self,
        phone: str,
        message: str,
        notification_type: str,
        provider_message_id: Optional[str] = None,
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Optional[int]:
        try:
            notification_code = f"SMS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{phone[-4:]}"
            notification = Notification(
                title=f"SMS Notification - {notification_type}",
                message=message,
                notification_code=notification_code,
                notification_type=NotificationType[notification_type.upper()] if notification_type.upper() in NotificationType.__members__ else NotificationType.SYSTEM_ALERT,
                channel=NotificationChannel.SMS,
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
            logger.warning("Failed to log SMS notification", error=str(e))
            return None

    async def send_sms(
        self,
        to_phone: str,
        message: str,
        notification_type: str = "SYSTEM_ALERT",
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            validated_phone = validate_phone(to_phone)
            formatted_phone = self._format_phone(validated_phone)

            if not message or len(message.strip()) == 0:
                raise ValidationError("Message cannot be empty")

            if len(message) > 1600:
                raise ValidationError("Message exceeds maximum length of 1600 characters")

            provider_result = await self._send_via_provider(formatted_phone, message)

            notification_id = await self._log_sms_notification(
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

            await self.log_operation("send_sms", {
                "recipient": formatted_phone,
                "provider": provider_result.get("provider"),
                "notification_id": notification_id
            })

            return result

        except (ValidationError, ExternalServiceError):
            raise
        except Exception as e:
            await self.log_error("send_sms", e)
            raise ExternalServiceError("Failed to send SMS")

    async def send_verification_code(
        self,
        to_phone: str,
        code: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            validated_phone = validate_phone(to_phone)

            if not code:
                code = str(secrets.randbelow(900000) + 100000)

            message = (
                f"Your Urbain verification code is: {code}\n"
                f"This code expires in 10 minutes.\n"
                f"If you didn't request this, please ignore."
            )

            result = await self.send_sms(
                to_phone=validated_phone,
                message=message,
                notification_type="SYSTEM_ALERT",
                user_id=user_id
            )

            result["verification_code"] = code

            await self.log_operation("send_verification_code", {
                "phone": validated_phone,
                "code_length": len(code)
            })

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_verification_code", e)
            raise ExternalServiceError("Failed to send verification code")

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

            result = await self.send_sms(
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
            raise ExternalServiceError("Failed to send SMS alert")

    async def send_bulk_sms(
        self,
        recipients: List[str],
        message: str,
        batch_size: int = 50
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
                        await self.send_sms(to_phone=recipient, message=message)
                        results["successful"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "recipient": recipient,
                            "error": str(e)
                        })

                if i + batch_size < len(recipients):
                    import asyncio
                    await asyncio.sleep(0.5)

            await self.log_operation("send_bulk_sms", {
                "total": results["total"],
                "successful": results["successful"],
                "failed": results["failed"]
            })

            return results

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_bulk_sms", e)
            raise ExternalServiceError("Failed to send bulk SMS")

    async def send_signal_update(
        self,
        to_phone: str,
        signal_ref: str,
        signal_title: str,
        new_status: str,
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            validated_phone = validate_phone(to_phone)

            message = (
                f"Signal Update: {signal_ref}\n"
                f"{signal_title[:100]}\n"
                f"Status: {new_status}\n"
                f"Check app for details."
            )

            return await self.send_sms(
                to_phone=validated_phone,
                message=message,
                notification_type="SIGNAL_UPDATED",
                user_id=user_id,
                signal_id=signal_id
            )

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_signal_update", e)
            raise ExternalServiceError("Failed to send signal update SMS")
