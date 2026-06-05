"""WebSocket pool for real-time VPN usage / bandwidth dashboard updates."""

import json
from typing import Any, List

from fastapi import WebSocket

from app.shared.logging_context import structured_extra
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class UsageConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: Any) -> None:
        if not self.active_connections:
            return
        message = json.dumps(data, default=str)
        dead: List[WebSocket] = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception as exc:
                logger.warning(
                    "Usage WebSocket broadcast send failed",
                    extra=structured_extra("usage_ws_send_failed", error=str(exc)),
                )
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


usage_ws_manager = UsageConnectionManager()
