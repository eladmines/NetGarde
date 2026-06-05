"""
WebSocket Connection Manager for real-time broadcasting.
Manages connected WebSocket clients and broadcasts messages to all of them.
"""

import json
from typing import Any, List

from fastapi import WebSocket

from app.shared.logging_context import structured_extra
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: Any):
        if not self.active_connections:
            return

        message = json.dumps(data, default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as exc:
                logger.warning(
                    "DNS WebSocket broadcast send failed",
                    extra=structured_extra("dns_ws_send_failed", error=str(exc)),
                )
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


ws_manager = ConnectionManager()
