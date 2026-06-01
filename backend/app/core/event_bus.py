import structlog
import asyncio
from typing import Callable, Dict, List, Any, Awaitable, Optional
from enum import Enum
from collections import defaultdict

logger = structlog.get_logger()


class EventType(str, Enum):
    SIGNAL_CREATED = "signal.created"
    SIGNAL_UPDATED = "signal.updated"
    SIGNAL_STATE_CHANGED = "signal.state_changed"
    SIGNAL_RESOLVED = "signal.resolved"
    SIGNAL_DELETED = "signal.deleted"
    SIGNAL_ESCALATED = "signal.escalated"
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"
    REPORT_GENERATED = "report.generated"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_ROLE_CHANGED = "user.role_changed"
    AUDIT_LOG_CREATED = "audit_log.created"


EventHandler = Callable[..., Awaitable[None]]


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._once_handlers: Dict[str, List[EventHandler]] = defaultdict(list)

    def on(self, event_type: str, handler: EventHandler):
        self._handlers[event_type].append(handler)
        logger.debug("Handler registered", event_type=event_type, handler=handler.__name__)

    def once(self, event_type: str, handler: EventHandler):
        self._once_handlers[event_type].append(handler)

    def off(self, event_type: str, handler: EventHandler):
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    async def emit(self, event_type: str, **kwargs):
        logger.info("Event emitted", event_type=event_type, data=kwargs)
        handlers = list(self._handlers.get(event_type, []))
        once_handlers = list(self._once_handlers.get(event_type, []))

        results = []
        for handler in handlers:
            try:
                result = handler(**kwargs)
                if asyncio.iscoroutine(result):
                    result = await result
                results.append(result)
            except Exception as e:
                logger.error("Handler failed", event_type=event_type, handler=handler.__name__, error=str(e))

        for handler in once_handlers:
            try:
                result = handler(**kwargs)
                if asyncio.iscoroutine(result):
                    result = await result
                results.append(result)
            except Exception as e:
                logger.error("Once handler failed", event_type=event_type, handler=handler.__name__, error=str(e))
            self._once_handlers[event_type].remove(handler)

        return results


event_bus = EventBus()
