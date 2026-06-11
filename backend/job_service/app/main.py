"""Job Service - FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.logging import get_logger, setup_logging
from shared.middleware import setup_metrics

from .api.router import api_router

setup_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Job Service",
        description="Job scraping engine that discovers, normalizes, and stores jobs from multiple sources",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
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
    setup_metrics(app, "job")

    @app.on_event("startup")
    async def startup() -> None:
        logger.info("Job Service starting up...")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        logger.info("Job Service shutting down...")

    return app


app = create_app()
