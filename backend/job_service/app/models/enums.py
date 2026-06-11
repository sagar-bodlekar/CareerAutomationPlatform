"""Job service enums."""

import enum


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    OTHER = "other"


class JobStatus(str, enum.Enum):
    ACTIVE = "active"
    FILLED = "filled"
    EXPIRED = "expired"
    DRAFT = "draft"
    CLOSED = "closed"


class SalaryCurrency(str, enum.Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CNY = "CNY"
    OTHER = "OTHER"


class SourceType(str, enum.Enum):
    API = "api"
    RSS = "rss"
    SCRAPE = "scrape"
    MANUAL = "manual"
    AGGREGATOR = "aggregator"


class LocationType(str, enum.Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class RemoteType(str, enum.Enum):
    FULLY_REMOTE = "fully_remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class ExperienceLevel(str, enum.Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"
