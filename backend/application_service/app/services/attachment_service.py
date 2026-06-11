"""Attachment service for resume PDF handling."""

import logging
from typing import Optional

from shared.config import settings

logger = logging.getLogger(__name__)


class AttachmentService:
    """Service for downloading and managing resume PDF attachments."""

    async def download_resume_pdf(self, resume_file_id: int) -> Optional[bytes]:
        """Download resume PDF from MinIO.

        Args:
            resume_file_id: ID of the resume file record (expected to have
                a matching file in MinIO under resumes/ bucket).

        Returns:
            PDF bytes or None if not found.
        """
        try:
            from minio import Minio

            client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_use_ssl,
            )

            object_path = f"resumes/{resume_file_id}.pdf"
            response = client.get_object(settings.minio_resumes_bucket, object_path)
            data = response.read()
            response.close()
            response.release_conn()

            if data:
                logger.info("Resume PDF downloaded from MinIO", file_id=resume_file_id, size=len(data))
                return data

            logger.warning("Resume PDF not found in MinIO", file_id=resume_file_id)
            return None

        except Exception as e:
            logger.error("Failed to download resume PDF from MinIO: %s", str(e), exc_info=True)
            return None

    async def attach_to_email(self, pdf_bytes: bytes, filename: str = "resume.pdf") -> Optional[dict]:
        """Create MIME attachment from PDF bytes.

        Args:
            pdf_bytes: Raw PDF file bytes.
            filename: Name for the attachment.

        Returns:
            Dict with attachment metadata for MIME email, or None if no data.
        """
        if not pdf_bytes:
            return None

        import base64
        encoded = base64.b64encode(pdf_bytes).decode()
        return {
            "filename": filename,
            "content": encoded,
            "content_type": "application/pdf",
            "encoding": "base64",
        }
