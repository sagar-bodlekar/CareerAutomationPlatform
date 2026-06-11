"""Job normalizer - maps varied source schemas to unified Job schema."""

from typing import Optional


class JobNormalizer:
    """Normalizes job data from different source formats into a standard schema.

    Handles field name mapping, data type coercion, and value standardization.
    """

    # Field mapping: source_field_name -> our_field_name
    COMMON_FIELD_MAP: dict[str, str] = {
        "title": "title",
        "position": "title",
        "job_title": "title",
        "role": "title",
        "name": "title",
        "company": "company_name",
        "company_name": "company_name",
        "employer": "company_name",
        "organization": "company_name",
        "description": "description",
        "job_description": "description",
        "body": "description",
        "summary": "description",
        "location": "location",
        "locations": "location",
        "city": "location",
        "office": "location",
        "url": "job_url",
        "job_url": "job_url",
        "link": "job_url",
        "apply_url": "apply_url",
        "application_url": "apply_url",
        "salary": "salary_raw",
        "compensation": "salary_raw",
        "pay": "salary_raw",
        "salary_range": "salary_raw",
        "type": "employment_type_raw",
        "employment_type": "employment_type_raw",
        "job_type": "employment_type_raw",
        "posted": "posted_at_raw",
        "posted_at": "posted_at_raw",
        "date": "posted_at_raw",
        "created_at": "posted_at_raw",
        "published": "posted_at_raw",
        "skills": "required_skills_raw",
        "required_skills": "required_skills_raw",
        "tags": "required_skills_raw",
        "keywords": "required_skills_raw",
        "experience": "experience_raw",
        "experience_required": "experience_raw",
        "min_experience": "experience_raw",
        "education": "education_required",
        "education_required": "education_required",
        "degree": "degree_preferred",
    }

    EMPLOYMENT_TYPE_MAP: dict[str, str] = {
        "full-time": "full_time",
        "fulltime": "full_time",
        "full_time": "full_time",
        "part-time": "part_time",
        "parttime": "part_time",
        "part_time": "part_time",
        "contract": "contract",
        "contractor": "contract",
        "temporary": "temporary",
        "temp": "temporary",
        "internship": "internship",
        "intern": "internship",
        "freelance": "freelance",
        "freelancer": "freelance",
        "other": "other",
    }

    LOCATION_TYPE_MAP: dict[str, str] = {
        "remote": "remote",
        "work from home": "remote",
        "wfh": "remote",
        "anywhere": "remote",
        "onsite": "onsite",
        "on-site": "onsite",
        "in office": "onsite",
        "in-office": "onsite",
        "hybrid": "hybrid",
    }

    def normalize(self, raw_job: dict) -> dict:
        """Normalize a raw job dict into standard JobCreate format.

        Args:
            raw_job: Raw job data from any source.

        Returns:
            Normalized job dict matching JobCreate schema.
        """
        normalized = {}

        # Map known fields
        for source_field, target_field in self.COMMON_FIELD_MAP.items():
            if source_field in raw_job and raw_job[source_field] is not None:
                normalized[target_field] = raw_job[source_field]

        # Standardize employment type
        emp_raw = normalized.pop("employment_type_raw", None)
        if emp_raw:
            emp_lower = str(emp_raw).lower().strip()
            normalized["employment_type"] = self.EMPLOYMENT_TYPE_MAP.get(emp_lower, emp_lower)

        # Standardize location type
        loc = normalized.get("location", "")
        if loc:
            loc_lower = str(loc).lower()
            for key, val in self.LOCATION_TYPE_MAP.items():
                if key in loc_lower:
                    normalized["location_type"] = val
                    normalized["is_remote"] = (val == "remote")
                    break

        # Ensure required fields
        normalized.setdefault("title", "Unknown Position")
        normalized.setdefault("company_name", "Unknown Company")
        normalized.setdefault("status", "active")

        # Clean up intermediate fields
        for key in ["salary_raw", "posted_at_raw", "required_skills_raw", "experience_raw"]:
            normalized.pop(key, None)

        return normalized

    def normalize_batch(self, raw_jobs: list[dict]) -> list[dict]:
        """Normalize a batch of raw jobs."""
        return [self.normalize(job) for job in raw_jobs]
