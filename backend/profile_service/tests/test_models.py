"""Tests for Profile Service SQLAlchemy models."""

import uuid
from datetime import date, datetime

import pytest

from app.models.enums import (
    DatePrecision,
    EmploymentType,
    LocationType,
    SkillProficiency,
    SocialPlatform,
)
from app.models.models import (
    Certification,
    Education,
    PersonalInfo,
    Project,
    Skill,
    SocialLink,
    UserProfile,
    WorkExperience,
)


class TestEnums:
    """Test enum values."""

    def test_skill_proficiency(self):
        assert SkillProficiency.BEGINNER.value == "beginner"
        assert SkillProficiency.EXPERT.value == "expert"

    def test_location_type(self):
        assert LocationType.REMOTE.value == "remote"
        assert LocationType.HYBRID.value == "hybrid"

    def test_employment_type(self):
        assert EmploymentType.FULL_TIME.value == "full_time"
        assert EmploymentType.CONTRACT.value == "contract"

    def test_social_platform(self):
        assert SocialPlatform.GITHUB.value == "github"
        assert SocialPlatform.LINKEDIN.value == "linkedin"

    def test_date_precision(self):
        assert DatePrecision.YEAR.value == "year"
        assert DatePrecision.DAY.value == "day"


class TestUserProfile:
    """Test UserProfile model."""

    def test_create_profile(self):
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            headline="Test Engineer",
            summary="A test profile",
            location_type=LocationType.REMOTE,
            open_to_work=True,
        )
        assert profile.id is not None
        assert profile.headline == "Test Engineer"
        assert profile.open_to_work is True

    def test_profile_str(self):
        profile = UserProfile(
            user_id=uuid.uuid4(),
            headline="Senior Dev",
        )
        assert str(profile.id) is not None

    def test_profile_defaults(self):
        profile = UserProfile(
            user_id=uuid.uuid4(),
            open_to_work=True,
            open_to_relocation=False,
            years_of_experience=0.0,
        )
        assert profile.open_to_work is True
        assert profile.open_to_relocation is False
        assert profile.years_of_experience == 0.0


class TestPersonalInfo:
    """Test PersonalInfo model."""

    def test_create_personal_info(self):
        profile = UserProfile(user_id=uuid.uuid4())
        info = PersonalInfo(
            profile=profile,
            full_name="John Doe",
            email="john@example.com",
            phone="+1-555-0100",
        )
        assert info.full_name == "John Doe"
        assert info.email == "john@example.com"
        assert info.profile_id == profile.id


class TestSkill:
    """Test Skill model."""

    def test_create_skill(self):
        profile = UserProfile(user_id=uuid.uuid4())
        skill = Skill(
            profile=profile,
            name="Python",
            proficiency=SkillProficiency.EXPERT,
            years_used=8,
            is_top_skill=True,
        )
        assert skill.name == "Python"
        assert skill.proficiency == SkillProficiency.EXPERT
        assert skill.is_top_skill is True


class TestWorkExperience:
    """Test WorkExperience model."""

    def test_create_experience(self):
        profile = UserProfile(user_id=uuid.uuid4())
        exp = WorkExperience(
            profile=profile,
            company_name="Acme Corp",
            job_title="Senior Engineer",
            start_date=date(2020, 1, 1),
            is_current=True,
            employment_type=EmploymentType.FULL_TIME,
        )
        assert exp.company_name == "Acme Corp"
        assert exp.job_title == "Senior Engineer"
        assert exp.is_current is True


class TestEducation:
    """Test Education model."""

    def test_create_education(self):
        profile = UserProfile(user_id=uuid.uuid4())
        edu = Education(
            profile=profile,
            institution="MIT",
            degree="B.S. Computer Science",
            start_date=date(2012, 9, 1),
            end_date=date(2016, 6, 1),
        )
        assert edu.institution == "MIT"
        assert edu.degree == "B.S. Computer Science"


class TestProject:
    """Test Project model."""

    def test_create_project(self):
        profile = UserProfile(user_id=uuid.uuid4())
        project = Project(
            profile=profile,
            name="Career Platform",
            description="AI-powered job search platform",
            technologies=["Python", "React", "PostgreSQL"],
        )
        assert project.name == "Career Platform"
        assert len(project.technologies) == 3


class TestCertification:
    """Test Certification model."""

    def test_create_certification(self):
        profile = UserProfile(user_id=uuid.uuid4())
        cert = Certification(
            profile=profile,
            name="AWS Solutions Architect",
            issuer="Amazon",
            does_not_expire=False,
        )
        assert cert.name == "AWS Solutions Architect"
        assert cert.does_not_expire is False


class TestSocialLink:
    """Test SocialLink model."""

    def test_create_social_link(self):
        profile = UserProfile(user_id=uuid.uuid4())
        link = SocialLink(
            profile=profile,
            platform=SocialPlatform.GITHUB,
            url="https://github.com/johndoe",
            is_primary=True,
        )
        assert link.platform == SocialPlatform.GITHUB
        assert link.is_primary is True
