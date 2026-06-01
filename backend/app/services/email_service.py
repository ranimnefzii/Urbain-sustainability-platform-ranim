"""
Email Service - Urbain Sustainability System
Service d'envoi d'emails asynchrones avec templates Jinja2
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from pathlib import Path

import structlog
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.core.exceptions import (
    ExternalServiceError,
    ValidationError,
    ServiceUnavailableError
)
from app.core.config import settings
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.schemas.notification import NotificationCreate
from app.services.base import BaseService
from app.utils.validators import validate_email

logger = structlog.get_logger()


class EmailService(BaseService):
    """
    Service d'envoi d'emails asynchrones avec templates
    Supporte les templates Jinja2, pièces jointes et envois groupés
    """

    TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "emails"

    def __init__(self, db):
        super().__init__(db)
        self.notification_repo = NotificationRepository(db, Notification)
        self._template_env = None
        self._smtp_connected = False

    @property
    def template_env(self) -> Environment:
        if self._template_env is None:
            if self.TEMPLATE_DIR.exists():
                self._template_env = Environment(
                    loader=FileSystemLoader(str(self.TEMPLATE_DIR)),
                    autoescape=True
                )
            else:
                self._template_env = Environment(autoescape=True)
        return self._template_env

    def _is_email_configured(self) -> bool:
        """Returns True only if SMTP credentials are present (real send mode)."""
        return all([
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            settings.EMAIL_FROM,
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD
        ])

    async def _render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**variables)
        except TemplateNotFound:
            return self._render_fallback(variables)
        except Exception as e:
            logger.warning("Template rendering failed", template=template_name, error=str(e))
            return self._render_fallback(variables)

    def _render_fallback(self, variables: Dict[str, Any]) -> str:
        title = variables.get("title", "Notification")
        message = variables.get("message", "")
        first_name = variables.get("first_name", "")
        content = f"<h2>{title}</h2>"
        if first_name:
            content += f"<p>Dear {first_name},</p>"
        content += f"<p>{message}</p>"
        content += "<hr><p>Urbain Sustainability System</p>"
        return content

    def _build_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        message["To"] = to_email
        message["Subject"] = subject

        if text_content:
            message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        if attachments:
            for attachment in attachments:
                try:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.get("content", b""))
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={attachment.get('filename', 'file')}"
                    )
                    message.attach(part)
                except Exception as e:
                    logger.warning("Failed to attach file", filename=attachment.get("filename"), error=str(e))

        return message

    async def _send_smtp(self, message: MIMEMultipart) -> bool:
        if not self._is_email_configured():
            logger.warning("Email config incomplete (missing SMTP_USERNAME/PASSWORD) — logging instead of sending")
            logger.info("Email content", to=message["To"], subject=message["Subject"])
            return True

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
                server.ehlo()
                if settings.SMTP_PORT == 587:
                    server.starttls()
                    server.ehlo()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAIL_FROM, message["To"], message.as_string())
            return True
        except smtplib.SMTPAuthenticationError:
            logger.warning("SMTP auth failed — falling back to log mode (check SMTP_USERNAME/PASSWORD)")
            logger.info("Email content", to=message["To"], subject=message["Subject"])
            return True
        except smtplib.SMTPException as e:
            logger.warning("SMTP error — falling back to log mode", error=str(e))
            logger.info("Email content", to=message["To"], subject=message["Subject"])
            return True
        except Exception as e:
            logger.warning("Email send failed — falling back to log mode", error=str(e))
            logger.info("Email content", to=message["To"], subject=message["Subject"])
            return True

    async def _log_notification(
        self,
        recipient: str,
        subject: str,
        body: str,
        notification_type: str,
        template_name: Optional[str] = None,
        template_variables: Optional[Dict] = None,
        signal_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Optional[int]:
        try:
            notification = Notification(
                title=subject,
                message=body,
                notification_code=f"EMAIL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{recipient[:8]}",
                notification_type=NotificationType[notification_type.upper()] if notification_type.upper() in NotificationType.__members__ else NotificationType.SYSTEM_ALERT,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.SENT,
                recipient_email=recipient,
                user_id=user_id,
                signal_id=signal_id,
                template_name=template_name,
                template_variables=template_variables
            )
            self.db.add(notification)
            await self.db.commit()
            return notification.id
        except Exception as e:
            logger.warning("Failed to log email notification", error=str(e))
            return None

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        notification_type: str = "SYSTEM_ALERT",
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            validated_email = validate_email(to_email)

            message = self._build_message(validated_email, subject, html_content, text_content, attachments)
            sent = await self._send_smtp(message)

            notification_id = await self._log_notification(
                recipient=validated_email,
                subject=subject,
                body=html_content,
                notification_type=notification_type,
                signal_id=signal_id,
                user_id=user_id
            )

            result = {
                "success": sent,
                "recipient": validated_email,
                "subject": subject,
                "notification_id": notification_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await self.log_operation("send_email", {
                "recipient": validated_email,
                "subject": subject,
                "notification_id": notification_id
            })

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_email", e)
            raise ExternalServiceError("Failed to send email")

    async def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        first_name: str = "User"
    ) -> Dict[str, Any]:
        try:
            validated_email = validate_email(to_email)

            subject = "Verify your email - Urbain Sustainability System"
            template_vars = {
                "first_name": first_name,
                "email": validated_email,
                "token": verification_token,
                "verification_url": f"{settings.APP_URL}/verify-email?token={verification_token}",
                "expiry_hours": 24,
                "title": "Email Verification"
            }

            html_content = await self._render_template("verification_email.html", template_vars)
            text_content = (
                f"Dear {first_name},\n\n"
                f"Please verify your email by clicking the link below:\n"
                f"{template_vars['verification_url']}\n\n"
                f"Your verification code: {verification_token}\n"
                f"This link expires in 24 hours.\n\n"
                f"Urbain Sustainability System"
            )

            return await self.send_email(
                to_email=validated_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                notification_type="EMAIL_VERIFICATION",
                user_id=None
            )

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_verification_email", e)
            raise ExternalServiceError("Failed to send verification email")

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        first_name: str = "User"
    ) -> Dict[str, Any]:
        try:
            validated_email = validate_email(to_email)

            subject = "Password Reset - Urbain Sustainability System"
            template_vars = {
                "first_name": first_name,
                "email": validated_email,
                "token": reset_token,
                "reset_url": f"{settings.APP_URL}/reset-password?token={reset_token}",
                "expiry_hours": 24,
                "title": "Password Reset Request"
            }

            html_content = await self._render_template("password_reset_email.html", template_vars)
            text_content = (
                f"Dear {first_name},\n\n"
                f"We received a request to reset your password.\n"
                f"Click the link below to reset it:\n"
                f"{template_vars['reset_url']}\n\n"
                f"Your reset token: {reset_token}\n"
                f"This link expires in 24 hours.\n\n"
                f"If you didn't request this, please ignore this email.\n\n"
                f"Urbain Sustainability System"
            )

            return await self.send_email(
                to_email=validated_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                notification_type="SYSTEM_ALERT",
                user_id=None
            )

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_password_reset_email", e)
            raise ExternalServiceError("Failed to send password reset email")

    async def send_signal_notification(
        self,
        to_email: str,
        signal_ref: str,
        signal_title: str,
        status: str,
        first_name: str = "User",
        user_id: Optional[int] = None,
        signal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            validated_email = validate_email(to_email)

            subject = f"Signal {signal_ref} - Status: {status}"
            template_vars = {
                "first_name": first_name,
                "signal_ref": signal_ref,
                "signal_title": signal_title,
                "status": status,
                "signal_url": f"{settings.APP_URL}/signals/{signal_ref}",
                "title": f"Signal Update - {signal_ref}"
            }

            html_content = await self._render_template("signal_notification.html", template_vars)
            text_content = (
                f"Dear {first_name},\n\n"
                f"Your signal {signal_ref} ({signal_title}) has been updated to: {status}\n"
                f"View details: {template_vars['signal_url']}\n\n"
                f"Urbain Sustainability System"
            )

            return await self.send_email(
                to_email=validated_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                notification_type="SIGNAL_UPDATED",
                user_id=user_id,
                signal_id=signal_id
            )

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_signal_notification", e)
            raise ExternalServiceError("Failed to send signal notification")

    async def send_report(
        self,
        to_email: str,
        report_title: str,
        report_summary: str,
        report_url: str,
        first_name: str = "User",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        try:
            validated_email = validate_email(to_email)

            subject = f"Report: {report_title}"
            template_vars = {
                "first_name": first_name,
                "report_title": report_title,
                "report_summary": report_summary,
                "report_url": report_url,
                "title": subject
            }

            html_content = await self._render_template("report_email.html", template_vars)
            text_content = (
                f"Dear {first_name},\n\n"
                f"Report: {report_title}\n"
                f"{report_summary}\n\n"
                f"View full report: {report_url}\n\n"
                f"Urbain Sustainability System"
            )

            return await self.send_email(
                to_email=validated_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments,
                notification_type="REPORT_GENERATED"
            )

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_report", e)
            raise ExternalServiceError("Failed to send report email")

    async def send_bulk_emails(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
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
                "errors": [],
                "batches": 0
            }

            for i in range(0, len(recipients), batch_size):
                batch = recipients[i:i + batch_size]
                results["batches"] += 1

                for recipient in batch:
                    try:
                        await self.send_email(
                            to_email=recipient,
                            subject=subject,
                            html_content=html_content,
                            text_content=text_content,
                            notification_type="SYSTEM_ALERT"
                        )
                        results["successful"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "recipient": recipient,
                            "error": str(e)
                        })

                if i + batch_size < len(recipients):
                    import asyncio
                    await asyncio.sleep(1)

            await self.log_operation("send_bulk_emails", {
                "total": results["total"],
                "successful": results["successful"],
                "failed": results["failed"]
            })

            return results

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_bulk_emails", e)
            raise ExternalServiceError("Failed to send bulk emails")

    async def send_welcome_email(
        self,
        to_email: str,
        first_name: str,
        username: str
    ) -> Dict[str, Any]:
        try:
            validated_email = validate_email(to_email)

            subject = "Welcome to Urbain Sustainability System!"
            template_vars = {
                "first_name": first_name,
                "username": username,
                "email": validated_email,
                "app_url": settings.APP_URL,
                "title": "Welcome Aboard!"
            }

            html_content = await self._render_template("welcome_email.html", template_vars)
            text_content = (
                f"Welcome {first_name}!\n\n"
                f"Thank you for joining Urbain Sustainability System.\n"
                f"Your username is: {username}\n\n"
                f"Get started: {settings.APP_URL}\n\n"
                f"Urbain Sustainability System"
            )

            return await self.send_email(
                to_email=validated_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                notification_type="SYSTEM_ALERT",
                user_id=None
            )

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_welcome_email", e)
            raise ExternalServiceError("Failed to send welcome email")

    async def send_status_update(
        self,
        to_email: str,
        entity_type: str,
        entity_ref: str,
        old_status: str,
        new_status: str,
        details: Optional[str] = None,
        first_name: str = "User"
    ) -> Dict[str, Any]:
        try:
            validated_email = validate_email(to_email)

            subject = f"{entity_type.title()} {entity_ref} - Status Changed to {new_status}"
            template_vars = {
                "first_name": first_name,
                "entity_type": entity_type,
                "entity_ref": entity_ref,
                "old_status": old_status,
                "new_status": new_status,
                "details": details or "",
                "title": subject
            }

            html_content = await self._render_template("status_update_email.html", template_vars)
            text_content = (
                f"Dear {first_name},\n\n"
                f"The status of {entity_type} {entity_ref} has changed:\n"
                f"From: {old_status}\n"
                f"To: {new_status}\n"
                f"{'Details: ' + details if details else ''}\n\n"
                f"Urbain Sustainability System"
            )

            return await self.send_email(
                to_email=validated_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                notification_type="SYSTEM_ALERT"
            )

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("send_status_update", e)
            raise ExternalServiceError("Failed to send status update email")


from datetime import datetime, timezone
