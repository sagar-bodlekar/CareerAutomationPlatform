"""Experience matcher - compares years and relevance of experience."""

from typing import Optional


class ExperienceMatcher:
    """Compares a candidate's experience against job requirements.

    Scores based on total years, relevance to the role,
    and seniority level alignment.
    """

    EXPERIENCE_LEVEL_MAP: dict[str, int] = {
        "entry": 0,
        "junior": 0,
        "mid": 1,
        "senior": 2,
        "lead": 3,
        "manager": 3,
        "head": 4,
        "director": 4,
        "executive": 5,
        "vp": 5,
        "c-level": 5,
        "cto": 5,
    }

    def compute_years_score(
        self,
        profile_years: Optional[float],
        required_min: Optional[int],
        required_max: Optional[int],
    ) -> float:
        """Score based on years of experience.

        - If profile_years >= required_min: 100 (meets/exceeds minimum)
        - If profile_years is 80% of required_min: 80
        - If profile_years is 50% of required_min: 50
        - If profile_years is < 50% of required_min: proportional

        Args:
            profile_years: Candidate's years of experience.
            required_min: Minimum years required.
            required_max: Maximum years desired (or None).

        Returns:
            Score 0-100.
        """
        if profile_years is None:
            return 50.0  # Unknown experience, neutral score

        if required_min is None and required_max is None:
            return 100.0  # No experience requirement

        if required_min is not None:
            if profile_years >= required_min:
                # Check if overqualified
                if required_max and profile_years > required_max * 1.5:
                    return 70.0  # Overqualified
                if required_max and profile_years > required_max:
                    return 85.0  # Slightly overqualified
                return 100.0  # Perfect fit

            ratio = profile_years / required_min
            if ratio >= 0.8:
                return 80.0
            elif ratio >= 0.5:
                return 60.0
            else:
                return max(10.0, ratio * 100)

        if required_max is not None:
            if profile_years <= required_max:
                return 100.0
            return max(50.0, 100 - (profile_years - required_max) * 10)

        return 100.0

    def compute_level_score(
        self,
        profile_level: Optional[str],
        job_level: Optional[str],
    ) -> float:
        """Score based on seniority level alignment.

        Args:
            profile_level: Candidate's seniority level.
            job_level: Job's required seniority level.

        Returns:
            Score 0-100.
        """
        if not job_level or not profile_level:
            return 75.0  # Neutral score when level unknown

        profile_lvl = self.EXPERIENCE_LEVEL_MAP.get(profile_level.lower(), -1)
        job_lvl = self.EXPERIENCE_LEVEL_MAP.get(job_level.lower(), -1)

        if profile_lvl == -1 or job_lvl == -1:
            return 75.0

        diff = profile_lvl - job_lvl

        if diff == 0:
            return 100.0  # Exact match
        elif diff == 1:
            return 90.0  # Slightly above
        elif diff == -1:
            return 80.0  # Slightly below
        elif diff >= 2:
            return 70.0  # Overqualified
        else:
            return 50.0  # Underqualified

    def compute(
        self,
        profile_years: Optional[float] = None,
        required_min: Optional[int] = None,
        required_max: Optional[int] = None,
        profile_level: Optional[str] = None,
        job_level: Optional[str] = None,
    ) -> dict:
        """Compute overall experience match score.

        Returns:
            Dict with score and details.
        """
        years_score = self.compute_years_score(profile_years, required_min, required_max)
        level_score = self.compute_level_score(profile_level, job_level)

        # Weight: years 60%, level 40%
        overall = years_score * 0.6 + level_score * 0.4

        return {
            "score": round(overall, 1),
            "years_score": years_score,
            "level_score": level_score,
            "profile_years": profile_years,
            "required_min": required_min,
            "required_max": required_max,
            "profile_level": profile_level,
            "job_level": job_level,
        }
