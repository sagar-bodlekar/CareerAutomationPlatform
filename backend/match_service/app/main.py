"""Match Service - FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.logging import get_logger, setup_logging
from shared.middleware import setup_metrics

from .api.router import api_router

setup_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Match Service",
        description="Job matching engine that scores profiles against jobs",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")
    setup_metrics(app, "match")

    @app.on_event("startup")
    async def startup():
        logger.info("Match Service starting up...")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Match Service shutting down...")

    return app


app = create_app()
