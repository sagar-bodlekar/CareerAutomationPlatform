"""Skills matcher - computes skill overlap between profile and job."""

from typing import Optional


class SkillsMatcher:
    """Computes skill match scores between a profile and job.

    Uses intersection-over-union for matched percentage and
    categorizes skills into matched, missing, and extra.
    """

    # Optional synonym map for normalizing skill names
    SKILL_SYNONYMS: dict[str, list[str]] = {
        "javascript": ["js", "es6", "ecmascript"],
        "typescript": ["ts"],
        "python": ["python3"],
        "react": ["reactjs", "react.js"],
        "node": ["nodejs", "node.js", "node.js"],
        "aws": ["amazon web services"],
        "gcp": ["google cloud platform", "google cloud"],
        "azure": ["microsoft azure"],
        "k8s": ["kubernetes"],
        "docker": ["containerization", "containers"],
    }

    def _normalize_skills(self, skills: list[str]) -> set[str]:
        """Normalize skill names for comparison."""
        normalized = set()
        for skill in skills:
            if not skill:
                continue
            s = skill.strip().lower()
            normalized.add(s)
            # Add synonyms
            for canonical, synonyms in self.SKILL_SYNONYMS.items():
                if s == canonical or s in synonyms:
                    normalized.add(canonical)
                    for syn in synonyms:
                        normalized.add(syn)
        return normalized

    def compute(
        self,
        profile_skills: Optional[list[str]],
        required_skills: Optional[list[str]],
        nice_to_have: Optional[list[str]] = None,
    ) -> dict:
        """Compute skill match between profile and job.

        Args:
            profile_skills: Skills from user profile.
            required_skills: Required skills from job posting.
            nice_to_have: Nice-to-have skills from job posting.

        Returns:
            Dict with scores, matched/missing/extra skills.
        """
        profile = self._normalize_skills(profile_skills or [])
        required = self._normalize_skills(required_skills or [])
        nice = self._normalize_skills(nice_to_have or [])

        if not required:
            return {
                "score": 100.0,
                "matched_skills": list(profile),
                "missing_skills": [],
                "extra_skills": [],
                "match_percentage": 100.0,
            }

        # Matched: profile skills that are in required
        matched_required = profile & required
        # Extra: profile skills not in required or nice
        extra = profile - required - nice
        # Missing: required skills not in profile
        missing = required - profile

        # Score: intersection over union of required + profile
        all_required_and_profile = required | profile
        if all_required_and_profile:
            iou_score = len(matched_required) / len(all_required_and_profile) * 100
        else:
            iou_score = 0.0

        # Coverage: what percentage of required skills are matched
        coverage = len(matched_required) / len(required) * 100 if required else 100.0

        # Bonus for nice-to-have skills
        matched_nice = profile & nice
        nice_bonus = (len(matched_nice) / len(nice) * 10) if nice else 0

        score = min(100.0, coverage * 0.8 + iou_score * 0.2 + nice_bonus)

        return {
            "score": round(score, 1),
            "matched_skills": sorted(matched_required),
            "missing_skills": sorted(missing),
            "extra_skills": sorted(extra),
            "matched_nice_to_have": sorted(matched_nice),
            "match_percentage": round(coverage, 1),
        }
