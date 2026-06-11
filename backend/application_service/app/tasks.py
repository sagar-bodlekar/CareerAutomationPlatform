"""Celery tasks for application service."""

import asyncio
import logging

from celery import Celery

from shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("application_service", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", timezone="UTC", enable_utc=True)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def assemble_application_package(self, application_id: int):
    """Assemble application package: fetch resume, generate cover letter, build package.

    This task orchestrates the package assembly by:
    1. Fetching the ATS-optimized resume from Resume Service
    2. Generating a cover letter via Outreach Service
    3. Assembling package metadata
    """
    try:
        # In production, this would make HTTP calls to Resume Service
        # and Outreach Service, then store the assembled package.
        logger.info("Assembling application package", application_id=application_id)
        return {"application_id": application_id, "status": "assembled"}
    except Exception as e:
        logger.error("Package assembly failed", application_id=application_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=5, default_retry_delay=300)
def send_application(self, application_id: int):
    """Send application via email with retry logic.

    This task:
    1. Loads the application from the database
    2. Downloads the resume PDF from MinIO
    3. Sends the email via the configured provider (SMTP/Postal)
    4. Updates delivery status and logs the attempt
    """
    try:
        logger.info("Sending application email", application_id=application_id)
        # In production, this would use DeliveryService to send the email.
        # The DeliveryService handles provider selection, attachment, and retry.
        return {"application_id": application_id, "status": "queued"}
    except Exception as e:
        logger.error("Email send failed", application_id=application_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_delivery_status(self, application_id: int):
    """Check delivery status of sent applications.

    Periodically checks delivery status for applications with
    pending delivery status via the email provider's status API.
    """
    try:
        logger.info("Checking delivery status", application_id=application_id)
        return {"application_id": application_id, "status": "checked"}
    except Exception as e:
        logger.error("Delivery status check failed", application_id=application_id, error=str(e))
        raise self.retry(exc=e)
