"""Integration tests for match service."""

from unittest.mock import AsyncMock, patch

import pytest


class TestMatchIntegration:
    """Integration-style tests for the match pipeline."""

    @pytest.mark.asyncio
    async def test_full_match_pipeline(self, sample_profile_data, sample_job_data):
        """Test full match pipeline: profile data -> score -> save."""
        from app.schemas.match import MatchScoreRequest
        from app.services.match_service import MatchService

        mock_db = AsyncMock()
        mock_db.flush = AsyncMock()
        mock_db.add = AsyncMock()
        mock_db.execute = AsyncMock()

        # Mock no existing match
        result_mock = AsyncMock()
        result_mock.scalar_one_or_none = AsyncMock(return_value=None)
        mock_db.execute.return_value = result_mock

        service = MatchService(db=mock_db)
        request = MatchScoreRequest(
            profile_id=1,
            job_id=1,
            profile_data=sample_profile_data,
            job_data=sample_job_data,
        )

        # Compute score
        score = await service.compute_score(request)
        assert score.overall_score > 0
        assert score.skills_score is not None
        assert score.experience_score is not None
        assert score.location_score is not None
        assert len(score.matched_skills) >= 3  # Python, FastAPI, PostgreSQL
        assert len(score.missing_skills) >= 1  # At least AWS

    @pytest.mark.asyncio
    async def test_skill_gaps_analysis(self, sample_profile_data, sample_job_data):
        """Test skill gap analysis component."""
        from app.services.skills_matcher import SkillsMatcher

        matcher = SkillsMatcher()
        result = matcher.compute(
            profile_skills=sample_profile_data["skills"],
            required_skills=sample_job_data["required_skills"],
        )

        assert len(result["matched_skills"]) >= 3
        assert len(result["missing_skills"]) >= 1

    @pytest.mark.asyncio
    async def test_experience_scoring(self):
        """Test experience scoring component."""
        from app.services.experience_matcher import ExperienceMatcher

        matcher = ExperienceMatcher()
        result = matcher.compute(
            profile_years=5,
            required_min=3,
            required_max=7,
            profile_level="senior",
            job_level="senior",
        )

        assert result["score"] >= 90  # Senior+senior, 5 years in 3-7 range
        assert result["years_score"] == 100.0
        assert result["level_score"] == 100.0

    @pytest.mark.asyncio
    async def test_location_scoring_remote(self):
        """Test remote job location scoring."""
        from app.services.location_matcher import LocationMatcher

        matcher = LocationMatcher()
        result = matcher.compute(
            profile_location="San Francisco",
            job_location="Remote",
            is_remote_job=True,
        )

        assert result["score"] == 100.0
        assert result["remote_compatible"] is True
