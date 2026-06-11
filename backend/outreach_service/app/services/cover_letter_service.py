"""Cover letter generation service."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.models import OutreachContent
from ..schemas.cover_letter import CoverLetterRequest, CoverLetterResponse

logger = logging.getLogger(__name__)


class CoverLetterService:
    """Generates and manages cover letters."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(
        self,
        request: CoverLetterRequest,
    ) -> CoverLetterResponse:
        """Generate a cover letter.

        Uses AI Orchestrator when use_ai=True, otherwise creates a draft.
        """
        if request.use_ai:
            ai_content = await self._call_ai_orchestrator(request)
            content = ai_content.get("body", "")
            subject = ai_content.get("subject", f"Application for {request.job_title}")
            tone_used = ai_content.get("tone_used", request.tone)
            ai_agent = "outreach_agent"
            tokens = ai_content.get("tokens_used")
        else:
            content = self._generate_draft(request)
            subject = f"Application for {request.job_title} position"
            tone_used = request.tone
            ai_agent = None
            tokens = None

        record = OutreachContent(
            content_type="cover_letter",
            profile_id=request.profile_id,
            job_id=request.job_id,
            application_id=request.application_id,
            subject=subject,
            body=content,
            tone=tone_used,
            target_role=request.job_title,
            company_name=request.company_name,
            ai_agent_used=ai_agent,
            tokens_used=tokens,
            status="draft",
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return CoverLetterResponse.model_validate(record)

    async def get(self, content_id: int) -> Optional[CoverLetterResponse]:
        """Get a cover letter by ID."""
        result = await self.db.execute(
            select(OutreachContent).where(
                OutreachContent.id == content_id,
                OutreachContent.content_type == "cover_letter",
            )
        )
        record = result.scalar_one_or_none()
        return CoverLetterResponse.model_validate(record) if record else None

    async def update(
        self, content_id: int, body: Optional[str] = None, status: Optional[str] = None
    ) -> Optional[CoverLetterResponse]:
        """Update a cover letter."""
        result = await self.db.execute(
            select(OutreachContent).where(OutreachContent.id == content_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            return None
        if body:
            record.body = body
            record.edit_count += 1
            record.version += 1
        if status:
            record.status = status
        await self.db.flush()
        await self.db.refresh(record)
        return CoverLetterResponse.model_validate(record)

    def _generate_draft(self, request: CoverLetterRequest) -> str:
        """Generate a simple draft cover letter without AI."""
        skills = ", ".join(request.skills or [])
        achievements = "\n".join(f"- {a}" for a in (request.achievements or []))
        return (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my strong interest in the {request.job_title} "
            f"position at {request.company_name}. With my background as "
            f"{request.current_role or 'a professional'}, I am confident that my "
            f"skills and experience make me an excellent candidate.\n\n"
            f"My key qualifications include: {skills}\n\n"
            f"{achievements}\n\n"
            f"I would welcome the opportunity to discuss how my background aligns "
            f"with the needs of {request.company_name}. Thank you for your consideration.\n\n"
            f"Sincerely,\n{request.candidate_name}"
        )

    async def _call_ai_orchestrator(self, request: CoverLetterRequest) -> dict:
        """Call the AI Orchestrator for cover letter generation.

        TODO: Wire to AI Orchestrator service when inter-service communication
        is set up in Phase 9 (Email Delivery & Tracking).
        POST /api/v1/ai/execute with agent_id="outreach", capability="cover_letter"
        to ai-orchestrator:8009.
        """
        # Placeholder: returns a draft until AI orchestration is wired
        return {
            "body": self._generate_draft(request),
            "subject": f"Application for {request.job_title}",
            "tone_used": request.tone,
            "tokens_used": None,
        }
