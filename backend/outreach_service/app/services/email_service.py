"""Email generation service."""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import OutreachContent
from ..schemas.email import EmailRequest, EmailResponse

logger = logging.getLogger(__name__)


class EmailService:
    """Generates and manages outreach emails."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(self, request: EmailRequest) -> EmailResponse:
        """Generate an outreach email."""
        if request.use_ai:
            ai_content = await self._call_ai_orchestrator(request)
            subject = ai_content.get("subject", f"Interest in {request.job_title} position")
            body = ai_content.get("body", "")
            tone_used = ai_content.get("tone_used", request.tone)
            ai_agent = "outreach_agent"
            tokens = ai_content.get("tokens_used")
        else:
            subject = f"Interest in {request.job_title} position"
            body = self._generate_draft(request)
            tone_used = request.tone
            ai_agent = None
            tokens = None

        record = OutreachContent(
            content_type="email",
            profile_id=request.profile_id,
            job_id=request.job_id,
            application_id=request.application_id,
            subject=subject,
            body=body,
            tone=tone_used,
            company_name=request.company_name,
            recipient_name=request.recipient_name,
            recipient_role=request.recipient_role,
            ai_agent_used=ai_agent,
            tokens_used=tokens,
            status="draft",
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return EmailResponse.model_validate(record)

    async def get(self, content_id: int) -> Optional[EmailResponse]:
        """Get an email by ID."""
        result = await self.db.execute(
            select(OutreachContent).where(
                OutreachContent.id == content_id,
                OutreachContent.content_type == "email",
            )
        )
        record = result.scalar_one_or_none()
        return EmailResponse.model_validate(record) if record else None

    async def update(
        self, content_id: int, subject: Optional[str] = None,
        body: Optional[str] = None, status: Optional[str] = None,
    ) -> Optional[EmailResponse]:
        """Update an email."""
        result = await self.db.execute(
            select(OutreachContent).where(OutreachContent.id == content_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            return None
        if subject:
            record.subject = subject
        if body:
            record.body = body
            record.edit_count += 1
            record.version += 1
        if status:
            record.status = status
        await self.db.flush()
        await self.db.refresh(record)
        return EmailResponse.model_validate(record)

    def _generate_draft(self, request: EmailRequest) -> str:
        """Generate a simple email draft."""
        recipient = request.recipient_name or "Hiring Manager"
        return (
            f"Dear {recipient},\n\n"
            f"I hope this message finds you well. I am writing to express my "
            f"interest in the {request.job_title} position at {request.company_name}.\n\n"
            f"As a {request.current_role or 'professional'}, I believe my "
            f"experience aligns well with this role. I have attached my resume "
            f"for your review.\n\n"
            f"I would welcome the opportunity to discuss my qualifications further. "
            f"Please let me know if you have any availability in the coming days.\n\n"
            f"Best regards,\n{request.candidate_name}"
        )

    async def _call_ai_orchestrator(self, request: EmailRequest) -> dict:
        """Call the AI Orchestrator for email generation.

        TODO: Wire to AI Orchestrator service when inter-service communication
        is set up in Phase 9 (Email Delivery & Tracking).
        POST /api/v1/ai/execute with agent_id="outreach", capability="email_generation"
        to ai-orchestrator:8009.
        """
        # Placeholder: returns a draft until AI orchestration is wired
        return {
            "body": self._generate_draft(request),
            "subject": f"Interest in {request.job_title} position",
            "tone_used": request.tone,
            "tokens_used": None,
        }
