"""WebSocket pool for real-time VPN usage / bandwidth dashboard updates."""

import json
import logging
from typing import Any, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class UsageConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Usage WebSocket connected (%s clients)", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("Usage WebSocket disconnected (%s clients)", len(self.active_connections))

    async def broadcast(self, data: Any) -> None:
        if not self.active_connections:
            return
        message = json.dumps(data, default=str)
        dead: List[WebSocket] = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception as exc:
                logger.warning("Usage WebSocket send failed: %s", exc)
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


usage_ws_manager = UsageConnectionManager()
