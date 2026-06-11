"""Package assembler for application bundles."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Application

logger = logging.getLogger(__name__)


class PackageAssembler:
    """Assembles application packages by fetching resume, cover letter, and email."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assemble(self, application: Application) -> dict:
        """Assemble a full application package.

        Fetches ATS-optimized resume, generates cover letter,
        generates email, and assembles metadata.

        Args:
            application: The application record.

        Returns:
            Dict with package metadata.
        """
        package = {
            "application_id": application.id,
            "job_id": application.job_id,
            "profile_id": application.profile_id,
            "company_name": application.company_name,
            "job_title": application.job_title,
            "components": {},
            "status": "assembling",
        }

        # Fetch resume from Resume Service
        resume = await self._fetch_resume(application.resume_id)
        if resume:
            package["components"]["resume"] = resume

        # These would be fetched from Outreach Service in production
        package["components"]["cover_letter"] = {"id": application.cover_letter_id}
        package["components"]["email"] = {"id": application.email_id}

        return package

    async def _fetch_resume(self, resume_id: Optional[int]) -> Optional[dict]:
        """Fetch resume from Resume Service."""
        if not resume_id:
            return None
        # TODO: Phase 7 - Make HTTP call to Resume Service
        return {"id": resume_id, "status": "available"}
