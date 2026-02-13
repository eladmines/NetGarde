"""
WebSocket Connection Manager for real-time broadcasting.
Manages connected WebSocket clients and broadcasts messages to all of them.
"""

import json
import logging
from typing import List, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and add it to the pool."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from the pool."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, data: Any):
        """Send data to all connected WebSocket clients."""
        if not self.active_connections:
            return

        message = json.dumps(data, default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


# Singleton instance — shared across the entire application
ws_manager = ConnectionManager()
