"""Celery tasks for outreach service."""

import asyncio
import logging

from celery import Celery

from shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("outreach_service", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", timezone="UTC", enable_utc=True)
