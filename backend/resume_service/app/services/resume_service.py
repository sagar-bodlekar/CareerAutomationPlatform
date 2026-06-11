"""Resume service — CRUD, generation, and ATS optimization orchestration."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Resume, ResumeFile, ResumeTemplate
from app.schemas.resume import ResumeCreate, ResumeSummary, ResumeUpdate
from app.schemas.generation import ATSOptimizeResponse, ATSScoreResponse


class ResumeService:
    """Service for resume CRUD and management."""

    LOAD_OPTIONS = [
        selectinload(Resume.files),
        selectinload(Resume.template),
    ]

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── CRUD ──────────────────────────────────────────────

    async def create_resume(self, user_id: uuid.UUID, data: ResumeCreate) -> Resume:
        """Create a new master resume."""
        resume = Resume(
            id=uuid.uuid4(),
            user_id=user_id,
            profile_id=data.profile_id,
            template_id=data.template_id,
            title=data.title,
            content=data.content or {},
            target_role=data.target_role,
            target_job_id=data.target_job_id,
            is_master=True,
            version=1,
        )
        self.session.add(resume)
        await self.session.flush()
        return resume

    async def get_resume(self, resume_id: uuid.UUID) -> Resume | None:
        """Get a resume by ID (excluding soft-deleted)."""
        result = await self.session.execute(
            select(Resume)
            .options(*self.LOAD_OPTIONS)
            .where(Resume.id == resume_id, Resume.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def update_resume(
        self, resume_id: uuid.UUID, data: ResumeUpdate, user_id: uuid.UUID
    ) -> Resume | None:
        """Update resume metadata/content."""
        resume = await self.get_resume(resume_id)
        if resume is None or resume.user_id != user_id:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(resume, field, value)

        resume.version += 1
        await self.session.flush()
        return resume

    async def soft_delete_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Soft delete a resume."""
        resume = await self.get_resume(resume_id)
        if resume is None or resume.user_id != user_id:
            return False
        resume.is_deleted = True
        await self.session.flush()
        return True

    async def list_resumes(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False,
    ) -> tuple[list[Resume], int]:
        """List resumes for a user with pagination."""
        query = (
            select(Resume)
            .options(selectinload(Resume.files))
            .where(Resume.user_id == user_id)
        )

        if not include_deleted:
            query = query.where(Resume.is_deleted.is_(False))

        # Count
        count_q = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_q)).scalar() or 0

        # Paginate
        query = query.order_by(Resume.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        resumes = list(result.scalars().all())

        return resumes, total

    def to_summary(self, resume: Resume) -> ResumeSummary:
        """Convert a Resume model to a summary."""
        return ResumeSummary(
            id=resume.id,
            user_id=resume.user_id,
            profile_id=resume.profile_id,
            title=resume.title,
            target_role=resume.target_role,
            is_master=resume.is_master,
            version=resume.version,
            ats_score=resume.ats_score,
            file_count=len(resume.files) if resume.files else 0,
            created_at=resume.created_at,
        )

    # ─── File Management ───────────────────────────────────

    async def get_resume_file(self, file_id: uuid.UUID) -> ResumeFile | None:
        """Get a resume file by ID."""
        return await self.session.get(ResumeFile, file_id)

    async def generate_presigned_url(self, file_id: uuid.UUID) -> str | None:
        """Generate a fresh presigned URL for a resume file."""
        from app.core.storage import storage

        resume_file = await self.get_resume_file(file_id)
        if resume_file is None:
            return None

        url = storage.get_presigned_url(resume_file.minio_object_key)
        resume_file.minio_presigned_url = url
        resume_file.presigned_url_expires_at = datetime.now(timezone.utc).replace(
            hour=datetime.now(timezone.utc).hour + 1
        )
        await self.session.flush()
        return url
