"""Location matcher - geographic proximity and remote compatibility."""

from typing import Optional


class LocationMatcher:
    """Scores location compatibility between candidate and job.

    Considers remote work preference, timezone overlap,
    and geographic proximity.
    """

    # Timezone offsets for major locations
    LOCATION_TIMEZONES: dict[str, float] = {
        "remote": 0,
        "san francisco": -8,
        "sf": -8,
        "bay area": -8,
        "new york": -5,
        "nyc": -5,
        "london": 0,
        "uk": 0,
        "berlin": 1,
        "germany": 1,
        "amsterdam": 1,
        "paris": 1,
        "france": 1,
        "bangkok": 7,
        "singapore": 8,
        "tokyo": 9,
        "sydney": 11,
        "bangalore": 5.5,
        "mumbai": 5.5,
        "delhi": 5.5,
        "india": 5.5,
        "dubai": 4,
        "toronto": -5,
        "vancouver": -8,
        "austin": -6,
        "seattle": -8,
        "portland": -8,
        "los angeles": -8,
        "la": -8,
        "chicago": -6,
        "denver": -7,
        "boston": -5,
    }

    def compute(
        self,
        profile_location: Optional[str] = None,
        job_location: Optional[str] = None,
        is_remote_job: bool = False,
        profile_prefers_remote: Optional[bool] = None,
    ) -> dict:
        """Compute location match score.

        Args:
            profile_location: Candidate's location.
            job_location: Job's location.
            is_remote_job: Whether the job is remote.
            profile_prefers_remote: Whether candidate prefers remote.

        Returns:
            Dict with score and details.
        """
        # Remote job - check if candidate can work remote
        if is_remote_job:
            if profile_prefers_remote is False:
                return {
                    "score": 70.0,
                    "proximity_score": 100.0,
                    "remote_compatible": True,
                    "details": "Remote job, candidate prefers onsite",
                }
            return {
                "score": 100.0,
                "proximity_score": 100.0,
                "remote_compatible": True,
                "details": "Remote job - fully compatible",
            }

        if not profile_location or not job_location:
            return {
                "score": 75.0,
                "proximity_score": 75.0,
                "remote_compatible": False,
                "details": "Location info incomplete",
            }

        # Check for timezone compatibility
        profile_tz = self._get_timezone(profile_location)
        job_tz = self._get_timezone(job_location)

        if profile_tz is not None and job_tz is not None:
            tz_diff = abs(profile_tz - job_tz)
            if tz_diff <= 1:
                proximity_score = 100.0
            elif tz_diff <= 3:
                proximity_score = 80.0
            elif tz_diff <= 6:
                proximity_score = 50.0
            else:
                proximity_score = 30.0
        else:
            # Check if location names have common words
            profile_words = set(profile_location.lower().split(","))
            job_words = set(job_location.lower().split(","))
            common = profile_words & job_words
            proximity_score = 70.0 if common else 50.0

        return {
            "score": round(proximity_score, 1),
            "proximity_score": round(proximity_score, 1),
            "remote_compatible": is_remote_job,
            "details": f"Profile: {profile_location}, Job: {job_location}",
        }

    def _get_timezone(self, location: str) -> Optional[float]:
        """Estimate timezone offset from location string."""
        if not location:
            return None

        location_lower = location.lower()

        # Check each known location
        for loc, tz in self.LOCATION_TIMEZONES.items():
            if loc in location_lower:
                return tz

        # Try to guess from country/continent
        if "europe" in location_lower or any(c in location_lower for c in ["france", "germany", "italy", "spain", "netherlands"]):
            return 1
        if "asia" in location_lower or any(c in location_lower for c in ["china", "japan", "korea", "india"]):
            return 8
        if "america" in location_lower or "united states" in location_lower:
            return -5
        if "australia" in location_lower:
            return 11
        if "africa" in location_lower:
            return 2

        return None
