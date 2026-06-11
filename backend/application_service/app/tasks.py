"""Celery tasks for application service."""

import logging
from celery import Celery

from shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("application_service", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", timezone="UTC", enable_utc=True)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def assemble_application_package(self, application_id: int):
    """Assemble application package asynchronously."""
    # TODO: Phase 9 - Implement async package assembly
    return {"application_id": application_id, "status": "assembled"}


@celery_app.task(bind=True, max_retries=5, default_retry_delay=300)
def send_application(self, application_id: int):
    """Send application via email."""
    # TODO: Phase 9 - Implement email delivery
    return {"application_id": application_id, "status": "queued"}
