"""Job service - CRUD and search operations."""

from typing import Optional

from sqlalchemy import Select, func, or_, select, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Job, JobSource
from ..schemas.filters import JobFilterParams
from ..schemas.job import JobCreate, JobUpdate
from ..schemas.source import JobSourceCreate, JobSourceUpdate


class JobService:
    """Service for job CRUD and search operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ─── Job CRUD ─────────────────────────────────────────

    async def create_job(self, data: JobCreate) -> Job:
        """Create a new job posting."""
        job = Job(**data.model_dump(exclude_unset=True))
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def get_job(self, job_id: int) -> Optional[Job]:
        """Get a job by ID."""
        result = await self.db.execute(
            select(Job).where(Job.id == job_id, Job.status != "closed")
        )
        return result.scalar_one_or_none()

    async def update_job(self, job_id: int, data: JobUpdate) -> Optional[Job]:
        """Update an existing job posting."""
        job = await self.get_job(job_id)
        if not job:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(job, key, value)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def delete_job(self, job_id: int) -> bool:
        """Soft-delete a job by setting status to closed."""
        job = await self.get_job(job_id)
        if not job:
            return False
        job.status = "closed"
        await self.db.flush()
        return True

    # ─── Search / List ────────────────────────────────────

    async def list_jobs(
        self, filters: JobFilterParams
    ) -> tuple[list[Job], int]:
        """List jobs with filtering, searching, and pagination."""
        query = select(Job).where(Job.status == (filters.status or "active"))

        # Apply filters
        if filters.query:
            search = f"%{filters.query}%"
            query = query.where(
                or_(
                    Job.title.ilike(search),
                    Job.company_name.ilike(search),
                    Job.description.ilike(search),
                    Job.requirements.ilike(search),
                    Job.required_skills.any(filters.query),
                )
            )

        if filters.title:
            query = query.where(Job.title.ilike(f"%{filters.title}%"))
        if filters.company_name:
            query = query.where(Job.company_name.ilike(f"%{filters.company_name}%"))
        if filters.skills:
            skill_list = [s.strip() for s in filters.skills.split(",")]
            for skill in skill_list:
                query = query.where(Job.required_skills.any(skill))
        if filters.location:
            query = query.where(Job.location.ilike(f"%{filters.location}%"))
        if filters.location_type:
            query = query.where(Job.location_type == filters.location_type)
        if filters.is_remote is not None:
            query = query.where(Job.is_remote == (1 if filters.is_remote else 0))
        if filters.experience_min is not None:
            query = query.where(Job.experience_min_years >= filters.experience_min)
        if filters.experience_max is not None:
            query = query.where(Job.experience_max_years <= filters.experience_max)
        if filters.experience_level:
            query = query.where(Job.experience_level == filters.experience_level)
        if filters.salary_min is not None:
            query = query.where(Job.salary_min >= filters.salary_min)
        if filters.salary_max is not None:
            query = query.where(Job.salary_max <= filters.salary_max)
        if filters.salary_currency:
            query = query.where(Job.salary_currency == filters.salary_currency)
        if filters.employment_type:
            query = query.where(Job.employment_type == filters.employment_type)
        if filters.industry:
            query = query.where(Job.industry == filters.industry)
        if filters.remote_type:
            query = query.where(Job.remote_type == filters.remote_type)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Sort
        sort_field = getattr(Job, filters.sort_by, Job.posted_at)
        order = sort_field.asc() if filters.sort_order == "asc" else sort_field.desc()
        query = query.order_by(order)

        # Paginate
        offset = (filters.page - 1) * filters.per_page
        query = query.offset(offset).limit(filters.per_page)

        result = await self.db.execute(query)
        jobs = list(result.scalars().all())

        return jobs, total

    async def upsert_job(self, data: JobCreate) -> tuple[Job, bool]:
        """Upsert a job based on external_id + source_id.

        Returns:
            Tuple of (job, created) where created is True if new.
        """
        if data.external_id and data.source_id:
            result = await self.db.execute(
                select(Job).where(
                    Job.external_id == data.external_id,
                    Job.source_id == data.source_id,
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in data.model_dump(exclude_unset=True, exclude={"external_id", "source_id"}).items():
                    setattr(existing, key, value)
                await self.db.flush()
                await self.db.refresh(existing)
                return existing, False

        return await self.create_job(data), True

    async def bulk_upsert(self, jobs_data: list[JobCreate]) -> tuple[list[Job], int]:
        """Bulk upsert jobs. Returns (jobs, created_count)."""
        jobs = []
        created_count = 0
        for data in jobs_data:
            job, created = await self.upsert_job(data)
            jobs.append(job)
            if created:
                created_count += 1
        return jobs, created_count

    # ─── Source CRUD ──────────────────────────────────────

    async def create_source(self, data: JobSourceCreate) -> JobSource:
        """Create a new job source configuration."""
        source = JobSource(**data.model_dump(exclude_unset=True))
        self.db.add(source)
        await self.db.flush()
        await self.db.refresh(source)
        return source

    async def get_source(self, source_id: int) -> Optional[JobSource]:
        """Get a job source by ID."""
        result = await self.db.execute(
            select(JobSource).where(JobSource.id == source_id)
        )
        return result.scalar_one_or_none()

    async def get_source_by_name(self, name: str) -> Optional[JobSource]:
        """Get a job source by name."""
        result = await self.db.execute(
            select(JobSource).where(JobSource.name == name)
        )
        return result.scalar_one_or_none()

    async def list_sources(self, active_only: bool = True) -> list[JobSource]:
        """List all job sources."""
        query = select(JobSource)
        if active_only:
            query = query.where(JobSource.is_active == 1)
        query = query.order_by(JobSource.priority)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_source(self, source_id: int, data: JobSourceUpdate) -> Optional[JobSource]:
        """Update a job source."""
        source = await self.get_source(source_id)
        if not source:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(source, key, value)
        await self.db.flush()
        await self.db.refresh(source)
        return source

    async def delete_source(self, source_id: int) -> bool:
        """Delete a job source."""
        source = await self.get_source(source_id)
        if not source:
            return False
        await self.db.delete(source)
        await self.db.flush()
        return True
