"""FastAPI application factory for Resume Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import settings
from shared.logging import get_logger, setup_logging

from app.api.router import api_router

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    app = FastAPI(
        title="Career Platform - Resume Service",
        description="Resume generation, PDF export, template management, "
        "and ATS optimization for the Career Automation Platform.",
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

    logger.info(
        "Resume Service started",
        service="resume-service",
        env=settings.app_env,
    )

    return app


app = create_app()
