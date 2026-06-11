"""Template service — CRUD for resume templates."""

import uuid
from pathlib import Path

import jinja2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ResumeTemplate
from app.schemas.template import ResumeTemplateCreate, ResumeTemplateUpdate


class TemplateService:
    """Service for managing resume templates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_template(self, data: ResumeTemplateCreate) -> ResumeTemplate:
        """Create a new resume template."""
        template = ResumeTemplate(
            id=uuid.uuid4(),
            name=data.name,
            display_name=data.display_name,
            description=data.description,
            html_content=data.html_content,
            css_content=data.css_content,
            thumbnail_url=data.thumbnail_url,
            is_default=data.is_default,
        )

        # If setting as default, unset any existing default
        if data.is_default:
            await self._unset_default()

        self.session.add(template)
        await self.session.flush()
        return template

    async def get_template(self, template_id: uuid.UUID) -> ResumeTemplate | None:
        """Get a template by ID."""
        return await self.session.get(ResumeTemplate, template_id)

    async def get_default_template(self) -> ResumeTemplate | None:
        """Get the default template."""
        result = await self.session.execute(
            select(ResumeTemplate).where(ResumeTemplate.is_default.is_(True))
        )
        return result.scalar_one_or_none()

    async def list_templates(self, active_only: bool = True) -> list[ResumeTemplate]:
        """List all templates, optionally filtering by active."""
        query = select(ResumeTemplate).order_by(ResumeTemplate.name)
        if active_only:
            query = query.where(ResumeTemplate.is_active.is_(True))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_template(
        self, template_id: uuid.UUID, data: ResumeTemplateUpdate
    ) -> ResumeTemplate | None:
        """Update a template."""
        template = await self.session.get(ResumeTemplate, template_id)
        if template is None:
            return None

        if data.is_default:
            await self._unset_default()

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(template, field, value)

        await self.session.flush()
        return template

    async def delete_template(self, template_id: uuid.UUID) -> bool:
        """Delete a template."""
        template = await self.session.get(ResumeTemplate, template_id)
        if template is None:
            return False
        await self.session.delete(template)
        await self.session.flush()
        return True

    async def seed_default_templates(self) -> list[ResumeTemplate]:
        """Seed default templates from files into the database."""
        templates_dir = Path(__file__).parent.parent / "templates" / "resumes"
        template_names = ["master.html", "modern.html", "classic.html", "minimal.html"]

        created = []
        for tmpl_file in template_names:
            name = tmpl_file.replace(".html", "")
            file_path = templates_dir / tmpl_file
            if not file_path.exists():
                continue

            # Check if already exists
            existing = await self.get_by_name(name)
            if existing:
                continue

            html_content = file_path.read_text()
            is_default = name == "master"

            template = ResumeTemplate(
                id=uuid.uuid4(),
                name=name,
                display_name=name.capitalize(),
                description=f"{name.capitalize()} resume template",
                html_content=html_content,
                is_active=True,
                is_default=is_default,
            )
            self.session.add(template)
            created.append(template)

        if created:
            await self.session.flush()

        return created

    async def get_by_name(self, name: str) -> ResumeTemplate | None:
        """Get a template by name."""
        result = await self.session.execute(
            select(ResumeTemplate).where(ResumeTemplate.name == name)
        )
        return result.scalar_one_or_none()

    async def _unset_default(self) -> None:
        """Unset the default flag on all templates."""
        await self.session.execute(
            ResumeTemplate.__table__.update().values(is_default=False)
        )
