"""FastAPI application factory for service template."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import settings
from shared.logging import get_logger, setup_logging
from shared.middleware import setup_metrics

from app.api.router import api_router

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    app = FastAPI(
        title=f"{settings.app_name} - Service Template",
        version="0.1.0",
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    setup_metrics(app, "service-template")

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "service-template"}

    logger.info("Service started", service="template", env=settings.app_env)

    return app


app = create_app()
