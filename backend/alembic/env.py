"""Async Alembic configuration for the Career Platform.

This env.py supports async database operations via asyncpg and
auto-detects SQLAlchemy models from the shared Base metadata.
"""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool

from shared.config import settings
from shared.database import Base

# Alembic Config object
config = context.config

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configure Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _load_service_models(service_name: str) -> None:
    """Load SQLAlchemy models from a service's app.models.models module.

    Each service defines models that inherit from shared Base. Importing the
    module registers table metadata on Base.metadata so Alembic can detect
    them.

    Since each service has its own 'app' package (e.g. profile_service/app/),
    we temporarily add the service directory to sys.path, import via the
    canonical 'app.models.models' path, then clean up sys.path and remove
    the cached 'app' modules to avoid conflicts with the next service.
    """
    import importlib

    service_dir = str(Path(__file__).parent.parent / service_name)
    models_init = Path(service_dir) / "app" / "models" / "models.py"
    if not models_init.exists():
        return

    # Clean any 'app' modules left from a previous service import
    for key in list(sys.modules.keys()):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]

    # Temporarily add this service's directory so 'app' resolves here
    sys.path.insert(0, service_dir)
    try:
        importlib.import_module("app.models.models")
    finally:
        sys.path.remove(service_dir)

    # Clean up 'app' modules again so the next service gets its own 'app'
    for key in list(sys.modules.keys()):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]


# MetaData for autogenerate support.
# Load all service models so Alembic can detect their table definitions.
_service_order = [
    "profile_service",   # Phase 2
    "auth_service",      # Phase 3
    "resume_service",    # Phase 4
    "job_service",       # Phase 5
    "match_service",     # Phase 6
    "ai_orchestrator",   # Phase 6
    "outreach_service",  # Phase 7
    "application_service",# Phase 7
    "tracking_service",  # Phase 9
]
for svc in _service_order:
    _load_service_models(svc)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given SQL string.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with a connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
