"""Prometheus metrics instrumentation for FastAPI applications."""

import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
except ImportError:
    # Stub when prometheus_client is not installed
    class _StubMetric:
        def labels(self, **kwargs):
            return self

        def inc(self, amount=1):
            pass

        def dec(self, amount=1):
            pass

        def observe(self, amount):
            pass

        def set(self, value):
            pass

        def track_inprogress(self):
            class _StubTracker:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return _StubTracker()

    def generate_latest():
        return b"# prometheus_client not installed"

    CONTENT_TYPE_LATEST = "text/plain"

    Counter = lambda name, desc, labelnames=(): _StubMetric()
    Histogram = lambda name, desc, labelnames=(), buckets=(): _StubMetric()
    Gauge = lambda name, desc, labelnames=(): _StubMetric()


# ─── Metrics Definitions ──────────────────────────────────────────

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["service", "method", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=["service", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

active_requests = Gauge(
    "active_requests",
    "Active HTTP requests",
    labelnames=["service"],
)

# ─── Business Metrics (optional, set by services) ────────────────

application_sent_total = Counter(
    "application_sent_total",
    "Total applications sent",
    labelnames=["service"],
)

application_delivered_total = Counter(
    "application_delivered_total",
    "Total applications delivered",
    labelnames=["service"],
)

application_delivery_failed_total = Counter(
    "application_delivery_failed_total",
    "Total application delivery failures",
    labelnames=["service"],
)

match_found_total = Counter(
    "match_found_total",
    "Total matches found",
    labelnames=["service"],
)

profile_created_total = Counter(
    "profile_created_total",
    "Total profiles created",
    labelnames=["service"],
)

resume_generated_total = Counter(
    "resume_generated_total",
    "Total resumes generated",
    labelnames=["service"],
)

interview_scheduled_total = Counter(
    "interview_scheduled_total",
    "Total interviews scheduled",
    labelnames=["service"],
)

# ─── AI Metrics ─────────────────────────────────────────────────

ai_requests_total = Counter(
    "ai_requests_total",
    "Total AI requests",
    labelnames=["agent", "provider"],
)

ai_token_usage_total = Counter(
    "ai_token_usage_total",
    "Total AI token usage",
    labelnames=["agent", "provider", "model"],
)

ai_generation_duration_seconds = Histogram(
    "ai_generation_duration_seconds",
    "AI generation duration in seconds",
    labelnames=["agent", "provider"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

ai_provider_fallback_total = Counter(
    "ai_provider_fallback_total",
    "AI provider fallback count",
    labelnames=["from", "to"],
)

# ─── Queue Metrics ──────────────────────────────────────────────

celery_queue_depth = Gauge(
    "celery_queue_depth",
    "Current queue depth",
    labelnames=["queue"],
)

celery_processed_tasks_total = Counter(
    "celery_processed_tasks_total",
    "Total processed tasks",
    labelnames=["queue", "task"],
)

celery_failed_tasks_total = Counter(
    "celery_failed_tasks_total",
    "Total failed tasks",
    labelnames=["queue", "task"],
)

celery_task_duration_seconds = Histogram(
    "celery_task_duration_seconds",
    "Task duration in seconds",
    labelnames=["queue", "task"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0),
)


class MetricsMiddleware:
    """FastAPI middleware that records HTTP request metrics."""

    def __init__(self, app: FastAPI, service_name: str = "unknown"):
        self.app = app
        self.service_name = service_name
        self.setup_metrics_route()

    def setup_metrics_route(self):
        """Add /metrics endpoint to the FastAPI app."""

        @self.app.get("/metrics")
        async def metrics_endpoint():
            return Response(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/unknown")

        # Skip metrics endpoint itself
        if path == "/metrics":
            return await self.app(scope, receive, send)

        active_requests.labels(service=self.service_name).inc()
        start = time.time()

        status_code = [200]

        async def _send(message):
            if message["type"] == "http.response.start":
                status_code[0] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, _send)
        finally:
            duration = time.time() - start
            active_requests.labels(service=self.service_name).dec()
            http_requests_total.labels(
                service=self.service_name,
                method=method,
                status=status_code[0],
            ).inc()
            http_request_duration_seconds.labels(
                service=self.service_name,
                method=method,
            ).observe(duration)


def setup_metrics(app: FastAPI, service_name: str = "unknown"):
    """Convenience function to add metrics to a FastAPI app."""
    MetricsMiddleware(app, service_name)
