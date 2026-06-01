from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "urbain_sustainability",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)


@celery_app.task
def send_email_task(to_email: str, subject: str, body: str) -> dict:
    return {"status": "sent", "to": to_email, "subject": subject}


@celery_app.task
def send_sms_task(phone_number: str, message: str) -> dict:
    return {"status": "sent", "to": phone_number, "message": message}


@celery_app.task
def send_push_task(user_id: int, title: str, body: str) -> dict:
    return {"status": "sent", "user_id": user_id, "title": title}


@celery_app.task
def generate_report_task(report_id: int, report_type: str) -> dict:
    return {"status": "generated", "report_id": report_id, "type": report_type}


@celery_app.task
def cleanup_expired_notifications_task() -> dict:
    return {"status": "completed", "action": "cleanup_expired_notifications"}


@celery_app.task
def process_ai_classification_task(signal_id: int) -> dict:
    return {"status": "completed", "signal_id": signal_id, "action": "ai_classification"}
