"""Title matcher - computes title similarity using keyword overlap."""

from typing import Optional, Set


class TitleMatcher:
    """Computes similarity between a candidate's current/past titles
    and a job title using keyword extraction and overlap scoring.
    """

    # Normalization mappings for common title variations
    TITLE_NORMALIZATIONS: dict[str, str] = {
        "software engineer": "software engineer",
        "software developer": "software engineer",
        "programmer": "software engineer",
        "swe": "software engineer",
        "full stack": "full stack developer",
        "fullstack": "full stack developer",
        "front end": "frontend developer",
        "frontend": "frontend developer",
        "back end": "backend developer",
        "backend": "backend developer",
        "devops": "devops engineer",
        "data scientist": "data scientist",
        "ml engineer": "machine learning engineer",
        "ai engineer": "machine learning engineer",
        "product manager": "product manager",
        "pm": "product manager",
        "engineering manager": "engineering manager",
        "tech lead": "tech lead",
        "principal engineer": "principal engineer",
        "staff engineer": "staff engineer",
        "senior engineer": "senior engineer",
        "junior engineer": "junior engineer",
        "intern": "intern",
    }

    # Keywords that indicate seniority
    SENIORITY_KEYWORDS: dict[str, int] = {
        "senior": 3,
        "sr": 3,
        "staff": 4,
        "principal": 5,
        "lead": 3,
        "head": 4,
        "director": 5,
        "vp": 6,
        "chief": 7,
        "junior": 1,
        "jr": 1,
        "associate": 2,
        "mid": 2,
        "intern": 0,
        "trainee": 0,
    }

    def _normalize_title(self, title: str) -> str:
        """Normalize a job title."""
        t = title.lower().strip()
        for variant, canonical in self.TITLE_NORMALIZATIONS.items():
            if variant in t:
                return canonical
        return t

    def _extract_keywords(self, title: str) -> Set[str]:
        """Extract meaningful keywords from a title."""
        t = title.lower().strip()
        # Remove common stop words
        stop_words = {"a", "an", "the", "of", "in", "for", "and", "or", "to", "with", "at", "ii", "iii", "iv"}
        # Split by common delimiters
        import re
        words = set(re.findall(r"[a-z0-9+#.-]+", t))
        return words - stop_words

    def _extract_seniority(self, title: str) -> int:
        """Extract seniority level from a title."""
        t = title.lower()
        for keyword, level in self.SENIORITY_KEYWORDS.items():
            if keyword in t:
                return level
        return 2  # Default to mid-level

    def compute(
        self,
        profile_titles: Optional[list[str]] = None,
        job_title: Optional[str] = None,
    ) -> dict:
        """Compute title match score between a profile and job.

        Args:
            profile_titles: List of candidate's current and past titles.
            job_title: Target job title.

        Returns:
            Dict with score and details.
        """
        if not profile_titles or not job_title:
            return {
                "score": 50.0,
                "details": "Missing title information",
            }

        normalized_job = self._normalize_title(job_title)
        job_keywords = self._extract_keywords(normalized_job)
        job_seniority = self._extract_seniority(job_title)

        best_score = 0.0
        best_match_title = ""
        all_scores = []

        for profile_title in profile_titles:
            if not profile_title:
                continue

            normalized_profile = self._normalize_title(profile_title)
            profile_keywords = self._extract_keywords(normalized_profile)
            profile_seniority = self._extract_seniority(profile_title)

            # Title base similarity (keyword overlap)
            if job_keywords and profile_keywords:
                overlap = len(job_keywords & profile_keywords)
                union = len(job_keywords | profile_keywords)
                keyword_score = (overlap / union) * 100 if union > 0 else 0
            else:
                keyword_score = 0

            # Seniority alignment
            seniority_diff = abs(profile_seniority - job_seniority)
            if seniority_diff <= 1:
                seniority_score = 100
            elif seniority_diff == 2:
                seniority_score = 70
            elif seniority_diff == 3:
                seniority_score = 50
            else:
                seniority_score = 30

            # Check for exact or contained match
            exact_match = normalized_profile == normalized_job
            contained_match = normalized_profile in normalized_job or normalized_job in normalized_profile

            bonus = 20 if exact_match else (10 if contained_match else 0)

            score = min(100.0, keyword_score * 0.5 + seniority_score * 0.3 + bonus)

            all_scores.append({
                "title": profile_title,
                "score": round(score, 1),
                "keyword_score": round(keyword_score, 1),
                "seniority_score": seniority_score,
            })

            if score > best_score:
                best_score = score
                best_match_title = profile_title

        return {
            "score": round(best_score, 1),
            "best_match_title": best_match_title,
            "all_title_scores": all_scores,
            "job_title": job_title,
            "seniority_alignment": "good" if best_score >= 70 else "moderate" if best_score >= 40 else "poor",
        }
