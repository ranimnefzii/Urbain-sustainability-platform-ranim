import structlog
import json
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket

logger = structlog.get_logger()


class ConnectionManager:
    def __init__(self):
        self._connections: Dict[str, Dict[int, WebSocket]] = {}
        self._user_connections: Dict[int, Set[str]] = {}

    async def connect(self, ws: WebSocket, channel: str, user_id: Optional[int] = None):
        await ws.accept()
        if channel not in self._connections:
            self._connections[channel] = {}
        connection_id = id(ws)
        self._connections[channel][connection_id] = ws
        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(channel)
        logger.info("WebSocket connected", channel=channel, user_id=user_id)

    async def disconnect(self, ws: WebSocket, channel: str, user_id: Optional[int] = None):
        connection_id = id(ws)
        if channel in self._connections:
            self._connections[channel].pop(connection_id, None)
        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(channel)
        logger.info("WebSocket disconnected", channel=channel, user_id=user_id)

    async def broadcast(self, channel: str, message: dict):
        if channel not in self._connections:
            return
        disconnected = []
        for cid, ws in self._connections[channel].items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(cid)
        for cid in disconnected:
            self._connections[channel].pop(cid, None)

    async def send_to_user(self, user_id: int, message: dict):
        if user_id not in self._user_connections:
            return
        for channel in self._user_connections[user_id]:
            if channel in self._connections:
                for ws in list(self._connections[channel].values()):
                    try:
                        await ws.send_json(message)
                    except Exception:
                        pass

    async def broadcast_signal_update(self, signal_id: int, data: dict):
        await self.broadcast("signals", {
            "type": "signal_update",
            "signal_id": signal_id,
            "data": data,
        })

    async def broadcast_notification(self, user_id: int, notification: dict):
        await self.send_to_user(user_id, {
            "type": "notification",
            "data": notification,
        })

    async def broadcast_admin_stats(self, stats: dict):
        await self.broadcast("admin", {
            "type": "stats_update",
            "data": stats,
        })


manager = ConnectionManager()
