"""Shared FastAPI middleware for cross-cutting concerns.

Includes:
- Prometheus metrics
- Rate limiting
- Response compression
- Request logging
"""

from .metrics import MetricsMiddleware, setup_metrics
from .rate_limit import RateLimitMiddleware
from .compression import CompressionMiddleware

__all__ = [
    "MetricsMiddleware",
    "setup_metrics",
    "RateLimitMiddleware",
    "CompressionMiddleware",
]
