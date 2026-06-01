import structlog
from app.core.event_bus import EventType, event_bus

logger = structlog.get_logger()


async def on_signal_created(payload: dict):
    signal_id = payload.get("signal_id")
    logger.info("Signal created — auto-processing triggered", signal_id=signal_id)
    # Future: push to AI classification queue or background task


async def on_signal_state_changed(payload: dict):
    signal_id = payload.get("signal_id")
    new_status = payload.get("new_status")
    logger.info("Signal state changed — triggering notifications", signal_id=signal_id, new_status=new_status)


async def on_signal_escalated(payload: dict):
    signal_id = payload.get("signal_id")
    new_level = payload.get("level")
    logger.info("Signal escalated — notifying admins", signal_id=signal_id, level=new_level)


async def on_notification_failed(payload: dict):
    notification_id = payload.get("notification_id")
    error = payload.get("error")
    logger.warning("Notification delivery failed", notification_id=notification_id, error=error)


def register_event_handlers():
    event_bus.on(EventType.SIGNAL_CREATED.value, on_signal_created)
    event_bus.on(EventType.SIGNAL_STATE_CHANGED.value, on_signal_state_changed)
    event_bus.on(EventType.SIGNAL_ESCALATED.value, on_signal_escalated)
    event_bus.on(EventType.NOTIFICATION_FAILED.value, on_notification_failed)
    logger.info("Event handlers registered", count=4)
