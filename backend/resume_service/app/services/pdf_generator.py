"""PDF generation engine — renders HTML templates to PDF via WeasyPrint."""

import logging
import uuid
from pathlib import Path

import jinja2
from weasyprint import HTML

from app.core.config import settings
from app.core.storage import storage
from app.models.models import Resume, ResumeFile
from app.services.content_assembler import ContentAssembler

logger = logging.getLogger(__name__)

# Jinja2 environment pointing to our template directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "resumes"
TEMPLATE_LOADER = jinja2.FileSystemLoader(str(TEMPLATES_DIR))
JINJA_ENV = jinja2.Environment(
    loader=TEMPLATE_LOADER,
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


class PDFGenerator:
    """Generates optimized PDF resumes from structured content."""

    def __init__(self) -> None:
        self.content_assembler = ContentAssembler()

    @property
    def available_templates(self) -> list[str]:
        """List available template names (without .html suffix)."""
        return ["master", "modern", "classic", "minimal"]

    async def render_html(
        self,
        resume: Resume,
        profile_data: dict,
        template_name: str = "master",
    ) -> str:
        """Render resume data into an HTML string using a Jinja2 template.

        Args:
            resume: The Resume model instance.
            profile_data: Full profile dict from Profile Service.
            template_name: One of ``master``, ``modern``, ``classic``, ``minimal``.

        Returns:
            Rendered HTML string.
        """
        if template_name not in self.available_templates:
            template_name = "master"

        template = JINJA_ENV.get_template(f"{template_name}.html")

        # Build content from profile data, merge with any custom resume content
        resume_content = self.content_assembler.from_profile(profile_data)
        if resume.content:
            resume_content.update(resume.content)

        # Add template styling variables
        ctx = {
            **resume_content,
            "font_family": "Helvetica, Arial, sans-serif",
            "font_size": "11pt",
            "accent_color": "#2563eb",  # Blue-600
            "skill_style": "pill",
            "page_margin": "2cm 2cm 2cm 2cm",
            "background_color": "#ffffff",
            "header_align": "center",
            "sidebar_bg": "#f8fafc",
        }
        if resume_content.get("styles"):
            ctx.update(resume_content["styles"])

        return template.render(**ctx)

    async def generate_pdf(
        self,
        resume: Resume,
        profile_data: dict,
        template_name: str = "master",
    ) -> bytes:
        """Generate a PDF from resume data.

        Args:
            resume: The Resume model instance.
            profile_data: Full profile dict.
            template_name: Template to use.

        Returns:
            PDF bytes.
        """
        html_str = await self.render_html(resume, profile_data, template_name)
        pdf_bytes = HTML(string=html_str).write_pdf()
        return pdf_bytes

    async def generate_and_store_pdf(
        self,
        resume: Resume,
        profile_data: dict,
        session,
        template_name: str = "master",
        filename: str | None = None,
    ) -> ResumeFile:
        """Generate a PDF, upload to MinIO, and create a ResumeFile record.

        Args:
            resume: The Resume model instance.
            profile_data: Full profile dict.
            session: SQLAlchemy async session.
            template_name: Template to use.
            filename: Optional filename (auto-generated if omitted).

        Returns:
            The created ResumeFile model instance.
        """
        pdf_bytes = await self.generate_pdf(resume, profile_data, template_name)

        # Upload to MinIO
        upload_info = storage.upload_pdf(
            pdf_data=pdf_bytes,
            resume_id=resume.id,
            filename=filename or f"{resume.title.lower().replace(' ', '_')}.pdf",
        )

        # Generate presigned URL
        presigned_url = storage.get_presigned_url(upload_info["object_key"])

        from datetime import datetime, timezone, timedelta

        # Create ResumeFile record
        resume_file = ResumeFile(
            id=uuid.uuid4(),
            resume_id=resume.id,
            filename=upload_info["object_key"].split("/")[-1],
            file_size_bytes=upload_info["size_bytes"],
            content_type="application/pdf",
            minio_bucket=upload_info["bucket"],
            minio_object_key=upload_info["object_key"],
            minio_presigned_url=presigned_url,
            presigned_url_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            page_count=None,  # Could compute from PDF
        )
        session.add(resume_file)
        await session.flush()

        logger.info(
            "PDF generated and stored",
            resume_id=str(resume.id),
            object_key=upload_info["object_key"],
            size_bytes=upload_info["size_bytes"],
        )

        return resume_file
