"""Notification Service - FastAPI application with WebSocket support."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.logging import get_logger, setup_logging
from shared.middleware import setup_metrics

from .services.notification_service import NotificationService
from .services.websocket_service import manager

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info("Notification Service starting up...")
    yield
    logger.info("Notification Service shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Notification Service",
        description="Real-time notifications and WebSocket delivery",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    notif_service = NotificationService()

    @app.get("/api/v1/health")
    async def health():
        return {
            "status": "ok",
            "service": "notification-service",
            "version": "0.1.0",
        }

    @app.get("/api/v1/notifications")
    async def get_notifications(
        user_id: int,
        limit: int = 20,
        unread_only: bool = False,
    ):
        """Get notifications for a user."""
        notifications = await notif_service.get_notifications(
            user_id, limit=limit, unread_only=unread_only
        )
        return {"data": notifications}

    @app.get("/api/v1/notifications/unread/count")
    async def get_unread_count(user_id: int):
        """Get unread notification count."""
        count = await notif_service.get_unread_count(user_id)
        return {"data": {"count": count}}

    @app.post("/api/v1/notifications/{notification_id}/read")
    async def mark_as_read(notification_id: int, user_id: int):
        """Mark a notification as read."""
        success = await notif_service.mark_as_read(user_id, notification_id)
        return {"data": {"success": success}}

    @app.post("/api/v1/notifications/read-all")
    async def mark_all_as_read(user_id: int):
        """Mark all notifications as read."""
        count = await notif_service.mark_all_as_read(user_id)
        return {"data": {"marked": count}}

    @app.websocket("/ws/notifications/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: int):
        """WebSocket endpoint for real-time notifications."""
        await manager.connect(websocket, user_id)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await manager.disconnect(websocket, user_id)

    setup_metrics(app, "notification")
    return app


app = create_app()
