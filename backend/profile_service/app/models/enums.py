"""Enum types for Profile Service."""

import enum


class SkillProficiency(str, enum.Enum):
    """Skill proficiency level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LocationType(str, enum.Enum):
    """Type of location for work."""

    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"
    RELOCATE = "willing_to_relocate"


class EmploymentType(str, enum.Enum):
    """Type of employment."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    SELF_EMPLOYED = "self_employed"


class SocialPlatform(str, enum.Enum):
    """Social/professional platform."""

    LINKEDIN = "linkedin"
    GITHUB = "github"
    TWITTER = "twitter"
    STACKOVERFLOW = "stackoverflow"
    PORTFOLIO = "portfolio"
    DRIBBBLE = "dribbble"
    BEHANCE = "behance"
    MEDIUM = "medium"
    YOUTUBE = "youtube"
    OTHER = "other"


class DatePrecision(str, enum.Enum):
    """Precision of a date field."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"
