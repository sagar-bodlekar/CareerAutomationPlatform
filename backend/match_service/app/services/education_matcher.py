"""Education matcher - compares degree and field alignment."""

from typing import Optional


class EducationMatcher:
    """Compares a candidate's education against job requirements.

    Scores based on degree level, field of study alignment,
    and whether the education is required or preferred.
    """

    DEGREE_LEVELS: dict[str, int] = {
        "high school": 0,
        "associate": 1,
        "associate's": 1,
        "associates": 1,
        "bachelor": 2,
        "bachelor's": 2,
        "bachelors": 2,
        "bs": 2,
        "ba": 2,
        "bsc": 2,
        "master": 3,
        "master's": 3,
        "masters": 3,
        "ms": 3,
        "ma": 3,
        "msc": 3,
        "mba": 3,
        "phd": 4,
        "ph.d": 4,
        "doctorate": 4,
        "md": 4,
        "jd": 4,
    }

    # Field relevance mapping: profile_field -> job_field relevance
    FIELD_RELEVANCE: dict[str, list[str]] = {
        "computer science": ["computer science", "software engineering", "computer engineering", "data science", "information technology"],
        "software engineering": ["computer science", "software engineering", "computer engineering"],
        "data science": ["data science", "computer science", "statistics", "mathematics"],
        "business": ["business", "business administration", "management", "finance", "marketing"],
        "engineering": ["engineering", "computer engineering", "electrical engineering", "mechanical engineering"],
        "mathematics": ["mathematics", "statistics", "data science", "computer science"],
        "physics": ["physics", "engineering", "mathematics"],
    }

    def _normalize_degree(self, degree: Optional[str]) -> tuple[Optional[str], int]:
        """Normalize degree string to (field, level)."""
        if not degree:
            return None, -1

        degree_lower = degree.lower()

        # Extract level
        level = -1
        for name, lvl in self.DEGREE_LEVELS.items():
            if name in degree_lower:
                level = max(level, lvl)

        # Extract field (use remaining text after degree level)
        field = degree_lower
        for name in sorted(self.DEGREE_LEVELS.keys(), key=len, reverse=True):
            if name in field:
                field = field.replace(name, "").strip()
                break

        return field if field else None, level

    def compute(
        self,
        profile_education: Optional[list[str]] = None,
        required_education: Optional[str] = None,
        preferred_degree: Optional[str] = None,
    ) -> dict:
        """Compute education match score.

        Args:
            profile_education: List of candidate's degrees/certifications.
            required_education: Minimum education required for the job.
            preferred_degree: Preferred degree for the job.

        Returns:
            Dict with score and details.
        """
        if not required_education and not preferred_degree:
            return {
                "score": 100.0,
                "meets_requirement": True,
                "details": "No education requirement",
            }

        profile_education = profile_education or []
        req_field, req_level = self._normalize_degree(required_education)
        pref_field, pref_level = self._normalize_degree(preferred_degree)

        if not profile_education:
            return {
                "score": 30.0 if required_education else 70.0,
                "meets_requirement": False,
                "details": "No education info provided",
            }

        # Check each education entry against requirements
        best_level_match = -1
        best_field_match = False
        best_pref_match = False

        for edu in profile_education:
            field, level = self._normalize_degree(edu)

            if level > best_level_match:
                best_level_match = level

            if field and req_field:
                # Check field relevance
                for profile_field, relevant_fields in self.FIELD_RELEVANCE.items():
                    if profile_field in field and req_field in relevant_fields:
                        best_field_match = True
                        break
                if req_field in field:
                    best_field_match = True

            if preferred_degree and field:
                if pref_field and pref_field in field:
                    best_pref_match = True

        # Score computation
        score = 0.0

        if req_level >= 0:
            if best_level_match >= req_level:
                score += 50.0  # Meets minimum
                if best_field_match:
                    score += 30.0  # Relevant field
                else:
                    score += 15.0
            elif best_level_match >= 0:
                score += 25.0  # Has some education but below requirement
            else:
                score += 10.0
        else:
            score += 50.0  # No specific requirement

        if preferred_degree:
            if best_pref_match:
                score += 20.0
            elif best_level_match >= 0:
                score += 5.0

        return {
            "score": round(min(100.0, score), 1),
            "meets_requirement": best_level_match >= req_level,
            "profile_education": profile_education,
            "required_education": required_education,
            "preferred_degree": preferred_degree,
        }
