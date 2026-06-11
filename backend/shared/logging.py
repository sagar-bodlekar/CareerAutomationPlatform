"""Structured JSON logging configuration."""

import logging
import sys
from typing import Any

import structlog

from .config import settings


def setup_logging(*, log_level: str | None = None) -> None:
    """Configure structured JSON logging for the application.

    Args:
        log_level: Override log level (default: from settings).
    """
    level = (log_level or settings.log_level).upper()

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level),
    )

    # Suppress noisy loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str | None = None, **initial_values: Any) -> structlog.stdlib.BoundLogger:
    """Get a structured logger.

    Args:
        name: Logger name (typically __name__).
        **initial_values: Initial key-value pairs bound to the logger.

    Returns:
        A structlog BoundLogger instance.
    """
    return structlog.get_logger(name or __name__, **initial_values)
