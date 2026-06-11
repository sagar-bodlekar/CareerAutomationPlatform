"""Outreach template service."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import OutreachContent


class TemplateService:
    """Manages outreach templates for cover letters and emails."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_templates(self, content_type: Optional[str] = None) -> list[OutreachContent]:
        """List available templates."""
        query = select(OutreachContent).where(OutreachContent.is_template == 1)
        if content_type:
            query = query.where(OutreachContent.content_type == content_type)
        query = query.order_by(OutreachContent.template_name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_template(self, template_id: int) -> Optional[OutreachContent]:
        """Get a template by ID."""
        result = await self.db.execute(
            select(OutreachContent).where(
                OutreachContent.id == template_id,
                OutreachContent.is_template == 1,
            )
        )
        return result.scalar_one_or_none()

    async def create_template(
        self,
        name: str,
        content_type: str,
        body: str,
        tone: str = "professional",
        tags: Optional[list[str]] = None,
    ) -> OutreachContent:
        """Create a new template."""
        template = OutreachContent(
            content_type=content_type,
            body=body,
            tone=tone,
            is_template=1,
            template_name=name,
            tags=tags,
            status="draft",
        )
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return template
