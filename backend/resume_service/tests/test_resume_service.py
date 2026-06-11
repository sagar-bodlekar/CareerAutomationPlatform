"""Unit tests for Resume Service CRUD."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Resume
from app.schemas.resume import ResumeCreate
from app.services.resume_service import ResumeService


@pytest.mark.asyncio
async def test_create_resume(resume_service: ResumeService):
    """Test creating a master resume."""
    user_id = uuid.uuid4()
    data = ResumeCreate(
        user_id=user_id,
        profile_id=uuid.uuid4(),
        title="Master Resume",
    )
    resume = await resume_service.create_resume(user_id, data)
    assert resume.id is not None
    assert resume.title == "Master Resume"
    assert resume.is_master is True
    assert resume.version == 1


@pytest.mark.asyncio
async def test_get_resume(resume_service: ResumeService):
    """Test retrieving a resume."""
    user_id = uuid.uuid4()
    data = ResumeCreate(user_id=user_id, profile_id=uuid.uuid4())
    created = await resume_service.create_resume(user_id, data)

    retrieved = await resume_service.get_resume(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.asyncio
async def test_get_resume_not_found(resume_service: ResumeService):
    """Test getting non-existent resume returns None."""
    result = await resume_service.get_resume(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_update_resume(resume_service: ResumeService):
    """Test updating a resume."""
    user_id = uuid.uuid4()
    data = ResumeCreate(user_id=user_id, profile_id=uuid.uuid4(), title="Original")
    resume = await resume_service.create_resume(user_id, data)

    from app.schemas.resume import ResumeUpdate
    updated = await resume_service.update_resume(
        resume.id, ResumeUpdate(title="Updated Title"), user_id
    )
    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.version == 2


@pytest.mark.asyncio
async def test_update_resume_wrong_user(resume_service: ResumeService):
    """Test updating another user's resume returns None."""
    user_id = uuid.uuid4()
    data = ResumeCreate(user_id=user_id, profile_id=uuid.uuid4())
    resume = await resume_service.create_resume(user_id, data)

    from app.schemas.resume import ResumeUpdate
    result = await resume_service.update_resume(
        resume.id, ResumeUpdate(title="Hacked"), uuid.uuid4()
    )
    assert result is None


@pytest.mark.asyncio
async def test_soft_delete_resume(resume_service: ResumeService):
    """Test soft deleting a resume."""
    user_id = uuid.uuid4()
    data = ResumeCreate(user_id=user_id, profile_id=uuid.uuid4())
    resume = await resume_service.create_resume(user_id, data)

    deleted = await resume_service.soft_delete_resume(resume.id, user_id)
    assert deleted is True

    retrived = await resume_service.get_resume(resume.id)
    assert retrived is None  # Soft-deleted should not be returned


@pytest.mark.asyncio
async def test_list_resumes(resume_service: ResumeService):
    """Test listing resumes with pagination."""
    user_id = uuid.uuid4()
    for i in range(3):
        await resume_service.create_resume(
            user_id,
            ResumeCreate(user_id=user_id, profile_id=uuid.uuid4(), title=f"Resume {i}"),
        )

    resumes, total = await resume_service.list_resumes(user_id, page=1, page_size=10)
    assert len(resumes) == 3
    assert total == 3
