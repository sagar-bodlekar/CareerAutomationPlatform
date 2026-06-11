"""MinIO storage wrapper for resume file operations."""

import io
import uuid
from datetime import datetime, timedelta, timezone

from minio import Minio

from app.core.config import settings


class MinioStorage:
    """MinIO (S3-compatible) storage for resume PDFs."""

    def __init__(self) -> None:
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl,
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Ensure the resumes bucket exists."""
        bucket = settings.minio_resumes_bucket
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    def upload_pdf(
        self,
        pdf_data: bytes,
        resume_id: uuid.UUID,
        filename: str | None = None,
    ) -> dict:
        """Upload a PDF to MinIO and return metadata.

        Returns:
            Dict with ``bucket``, ``object_key``, ``size_bytes``.
        """
        bucket = settings.minio_resumes_bucket
        object_key = f"resumes/{resume_id}/{filename or f'{uuid.uuid4()}.pdf'}"

        pdf_stream = io.BytesIO(pdf_data)
        pdf_size = len(pdf_data)

        self.client.put_object(
            bucket_name=bucket,
            object_name=object_key,
            data=pdf_stream,
            length=pdf_size,
            content_type="application/pdf",
        )

        return {
            "bucket": bucket,
            "object_key": object_key,
            "size_bytes": pdf_size,
        }

    def get_presigned_url(self, object_key: str, expires_hours: int = 1) -> str:
        """Generate a presigned download URL for a PDF."""
        return self.client.presigned_get_object(
            bucket_name=settings.minio_resumes_bucket,
            object_name=object_key,
            expires=timedelta(hours=expires_hours),
        )

    def delete_object(self, object_key: str) -> None:
        """Delete a PDF from MinIO."""
        self.client.remove_object(
            bucket_name=settings.minio_resumes_bucket,
            object_name=object_key,
        )


# Global singleton
storage = MinioStorage()
