"""WebSocket service for real-time notification delivery via Redis pub-sub."""

import asyncio
import json
import logging
from typing import Optional

import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect

from shared.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a WebSocket connection for a user."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info("WebSocket connected", user_id=user_id)

        # Start listening for Redis pub-sub notifications
        asyncio.create_task(self._listen_redis(user_id))

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                w for w in self.active_connections[user_id] if w != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to all connections for a user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    await self.disconnect(connection, user_id)

    async def _listen_redis(self, user_id: int):
        """Listen for Redis pub-sub notifications for this user."""
        try:
            r = await self._get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe(f"notifications:{user_id}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await self.send_personal_message(data, user_id)
                    except (json.JSONDecodeError, Exception):
                        pass
        except Exception as e:
            logger.error("Redis pub-sub listener error", user_id=user_id, error=str(e))


manager = ConnectionManager()
