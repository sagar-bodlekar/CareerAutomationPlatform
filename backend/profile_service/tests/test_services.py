"""Unit tests for Profile Service business logic."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Skill, UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.skill import SkillCreate
from app.schemas.experience import WorkExperienceCreate
from app.services.profile_service import ProfileService


@pytest.mark.asyncio
async def test_create_profile(profile_service: ProfileService, db_session: AsyncSession):
    """Test creating a profile with nested data."""
    user_id = uuid.uuid4()
    data = ProfileCreate(
        headline="Test Engineer",
        summary="A test profile",
        location_city="Portland",
        location_country="USA",
        location_type="remote",
        preferred_roles=["Engineer"],
        open_to_work=True,
        years_of_experience=5.0,
        personal_info={
            "full_name": "Jane Smith",
            "email": "jane@example.com",
        },
        skills=[
            SkillCreate(name="Python", category="Language", proficiency="advanced"),
        ],
    )

    profile = await profile_service.create_profile(user_id, data)
    assert profile.id is not None
    assert profile.user_id == user_id
    assert profile.headline == "Test Engineer"
    assert profile.personal_info is not None
    assert profile.personal_info.full_name == "Jane Smith"
    assert len(profile.skills) == 1
    assert profile.skills[0].name == "Python"


@pytest.mark.asyncio
async def test_get_profile(profile_service: ProfileService):
    """Test retrieving a profile."""
    user_id = uuid.uuid4()
    data = ProfileCreate(headline="Get Test")
    profile = await profile_service.create_profile(user_id, data)

    retrieved = await profile_service.get_profile(profile.id)
    assert retrieved is not None
    assert retrieved.id == profile.id
    assert retrieved.headline == "Get Test"


@pytest.mark.asyncio
async def test_get_profile_not_found(profile_service: ProfileService):
    """Test retrieving a non-existent profile returns None."""
    result = await profile_service.get_profile(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_update_profile(profile_service: ProfileService):
    """Test updating a profile."""
    user_id = uuid.uuid4()
    data = ProfileCreate(headline="Original", summary="Original summary")
    profile = await profile_service.create_profile(user_id, data)

    update_data = ProfileUpdate(headline="Updated Headline")
    updated = await profile_service.update_profile(profile.id, update_data)
    assert updated is not None
    assert updated.headline == "Updated Headline"
    assert updated.summary == "Original summary"  # Unchanged


@pytest.mark.asyncio
async def test_delete_profile(profile_service: ProfileService):
    """Test deleting a profile."""
    user_id = uuid.uuid4()
    data = ProfileCreate(headline="Delete Test")
    profile = await profile_service.create_profile(user_id, data)

    deleted = await profile_service.delete_profile(profile.id)
    assert deleted is True

    retrieved = await profile_service.get_profile(profile.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_profile_not_found(profile_service: ProfileService):
    """Test deleting a non-existent profile returns False."""
    result = await profile_service.delete_profile(uuid.uuid4())
    assert result is False


@pytest.mark.asyncio
async def test_bulk_add_skills(profile_service: ProfileService):
    """Test bulk adding skills."""
    user_id = uuid.uuid4()
    profile = await profile_service.create_profile(user_id, ProfileCreate())

    skills_data = [
        SkillCreate(name="Python", category="Language"),
        SkillCreate(name="Docker", category="DevOps"),
        SkillCreate(name="AWS", category="Cloud"),
    ]
    skills = await profile_service.bulk_add_skills(profile.id, skills_data)
    assert len(skills) == 3
    assert skills[0].name == "Python"
    assert skills[1].profile_id == profile.id


@pytest.mark.asyncio
async def test_add_skill_not_found(profile_service: ProfileService):
    """Test adding a skill to non-existent profile returns None."""
    skill_data = SkillCreate(name="Python")
    result = await profile_service.add_skill(uuid.uuid4(), skill_data)
    assert result is None


@pytest.mark.asyncio
async def test_add_work_experience(profile_service: ProfileService):
    """Test adding work experience."""
    user_id = uuid.uuid4()
    profile = await profile_service.create_profile(user_id, ProfileCreate())

    from datetime import date
    exp_data = WorkExperienceCreate(
        company_name="Acme Corp",
        job_title="Senior Engineer",
        start_date=date(2020, 1, 1),
        is_current=True,
        description="Working on great things.",
    )
    exp = await profile_service.add_work_experience(profile.id, exp_data)
    assert exp is not None
    assert exp.company_name == "Acme Corp"
    assert exp.job_title == "Senior Engineer"
    assert exp.is_current is True


@pytest.mark.asyncio
async def test_get_profile_by_user(profile_service: ProfileService):
    """Test retrieving a profile by user ID."""
    user_id = uuid.uuid4()
    data = ProfileCreate(headline="User Lookup")
    await profile_service.create_profile(user_id, data)

    retrieved = await profile_service.get_profile_by_user(user_id)
    assert retrieved is not None
    assert retrieved.headline == "User Lookup"


@pytest.mark.asyncio
async def test_list_profiles(profile_service: ProfileService):
    """Test listing profiles with pagination."""
    for i in range(5):
        await profile_service.create_profile(
            uuid.uuid4(),
            ProfileCreate(headline=f"Profile {i}"),
        )

    profiles, total = await profile_service.list_profiles(page=1, page_size=3)
    assert len(profiles) == 3
    assert total == 5


@pytest.mark.asyncio
async def test_analytics(profile_service: ProfileService):
    """Test profile analytics."""
    user_id = uuid.uuid4()
    data = ProfileCreate(
        headline="Analytics Test",
        years_of_experience=10.0,
        skills=[
            SkillCreate(name="Python", category="Language", proficiency="expert"),
            SkillCreate(name="React", category="Framework", proficiency="advanced"),
            SkillCreate(name="Go", category="Language", proficiency="intermediate"),
        ],
    )
    profile = await profile_service.create_profile(user_id, data)

    analytics = await profile_service.get_analytics(profile.id)
    assert analytics is not None
    assert analytics.total_skills == 3
    assert len(analytics.top_skills) == 2  # expert + advanced
    assert "Python" in analytics.top_skills
    assert analytics.years_of_experience == 10.0
    assert "Language" in analytics.skill_categories
    assert analytics.skill_categories["Language"] == 2


@pytest.mark.asyncio
async def test_analytics_not_found(profile_service: ProfileService):
    """Test analytics for non-existent profile returns None."""
    result = await profile_service.get_analytics(uuid.uuid4())
    assert result is None
