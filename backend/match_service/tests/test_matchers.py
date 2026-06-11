"""Unit tests for match matchers."""


class TestSkillsMatcher:
    """Tests for SkillsMatcher."""

    def test_perfect_match(self):
        """Perfect skill overlap should score 100."""
        from app.services.skills_matcher import SkillsMatcher
        matcher = SkillsMatcher()
        result = matcher.compute(
            profile_skills=["Python", "React"],
            required_skills=["Python", "React"],
        )
        assert result["score"] == 100.0
        assert len(result["matched_skills"]) == 2
        assert len(result["missing_skills"]) == 0

    def test_no_match(self):
        """No overlap should score 0."""
        matcher = SkillsMatcher()
        result = matcher.compute(
            profile_skills=["Python"],
            required_skills=["Java", "C++"],
        )
        assert result["score"] == 0.0
        assert len(result["missing_skills"]) == 2

    def test_partial_match(self):
        """Partial overlap should score between 0-100."""
        matcher = SkillsMatcher()
        result = matcher.compute(
            profile_skills=["Python", "React", "Docker"],
            required_skills=["Python", "Java", "AWS"],
        )
        assert 0 < result["score"] < 100
        assert "Python" in result["matched_skills"]
        assert "Java" in result["missing_skills"]

    def test_empty_requirements(self):
        """No required skills should score 100."""
        matcher = SkillsMatcher()
        result = matcher.compute(
            profile_skills=["Python"],
            required_skills=[],
        )
        assert result["score"] == 100.0

    def test_nice_to_have_bonus(self):
        """Nice-to-have skills should add bonus."""
        matcher = SkillsMatcher()
        without_bonus = matcher.compute(
            profile_skills=["Python"],
            required_skills=["Python", "Java"],
            nice_to_have=[],
        )
        with_bonus = matcher.compute(
            profile_skills=["Python", "Docker"],
            required_skills=["Python", "Java"],
            nice_to_have=["Docker"],
        )
        assert with_bonus["score"] >= without_bonus["score"]

    def test_skill_synonyms(self):
        """Synonym skills should match."""
        matcher = SkillsMatcher()
        result = matcher.compute(
            profile_skills=["JS"],
            required_skills=["javascript"],
        )
        assert "js" in result["matched_skills"] or "javascript" in result["matched_skills"]

    def test_extra_skills(self):
        """Profile skills not in requirements should be returned as extra."""
        matcher = SkillsMatcher()
        result = matcher.compute(
            profile_skills=["Python", "React", "Go"],
            required_skills=["Python", "Java"],
        )
        assert "Go" in result["extra_skills"]


class TestExperienceMatcher:
    """Tests for ExperienceMatcher."""

    def test_meets_minimum(self):
        """Experience >= minimum should score 100."""
        from app.services.experience_matcher import ExperienceMatcher
        matcher = ExperienceMatcher()
        result = matcher.compute_years_score(5, 3, 7)
        assert result == 100.0

    def test_below_minimum(self):
        """Experience below minimum should score proportionally."""
        matcher = ExperienceMatcher()
        result = matcher.compute_years_score(2, 5, 10)
        assert result < 100.0
        assert result > 0

    def test_overqualified(self):
        """Significantly overqualified should reduce score."""
        matcher = ExperienceMatcher()
        result = matcher.compute_years_score(15, 3, 5)
        assert result < 100.0

    def test_no_requirement(self):
        """No experience requirement should score 100."""
        matcher = ExperienceMatcher()
        result = matcher.compute_years_score(5, None, None)
        assert result == 100.0

    def test_level_exact_match(self):
        """Same level should score 100."""
        matcher = ExperienceMatcher()
        result = matcher.compute_level_score("senior", "senior")
        assert result == 100.0

    def test_level_slightly_below(self):
        """One level below should score 80."""
        matcher = ExperienceMatcher()
        result = matcher.compute_level_score("mid", "senior")
        assert result == 80.0

    def test_level_overqualified(self):
        """Two levels above should score 70."""
        matcher = ExperienceMatcher()
        result = matcher.compute_level_score("director", "mid")
        assert result == 70.0

    def test_overall_composite(self):
        """Overall should combine years and level scores."""
        matcher = ExperienceMatcher()
        result = matcher.compute(
            profile_years=5,
            required_min=3,
            profile_level="senior",
            job_level="senior",
        )
        assert 0 < result["score"] <= 100
        assert "years_score" in result
        assert "level_score" in result


class TestLocationMatcher:
    """Tests for LocationMatcher."""

    def test_remote_job(self):
        """Remote job should score 100."""
        from app.services.location_matcher import LocationMatcher
        matcher = LocationMatcher()
        result = matcher.compute(
            profile_location="Remote",
            job_location="Remote",
            is_remote_job=True,
        )
        assert result["score"] == 100.0

    def test_same_timezone(self):
        """Same timezone should score 100."""
        matcher = LocationMatcher()
        result = matcher.compute(
            profile_location="New York",
            job_location="Boston",
            is_remote_job=False,
        )
        assert result["score"] == 100.0

    def test_different_timezone(self):
        """Different timezone should reduce score."""
        matcher = LocationMatcher()
        result = matcher.compute(
            profile_location="New York",
            job_location="Tokyo",
            is_remote_job=False,
        )
        assert result["score"] < 100.0


class TestEducationMatcher:
    """Tests for EducationMatcher."""

    def test_meets_requirement(self):
        """Education matching requirement should score well."""
        from app.services.education_matcher import EducationMatcher
        matcher = EducationMatcher()
        result = matcher.compute(
            profile_education=["BS Computer Science"],
            required_education="Bachelor's Degree",
        )
        assert result["meets_requirement"]
        assert result["score"] > 50

    def test_no_requirement(self):
        """No education requirement should score 100."""
        matcher = EducationMatcher()
        result = matcher.compute(profile_education=["BS"])
        assert result["score"] == 100.0

    def test_no_education(self):
        """No education info should score low."""
        matcher = EducationMatcher()
        result = matcher.compute(
            profile_education=[],
            required_education="Bachelor's Degree",
        )
        assert result["meets_requirement"] is False


class TestTitleMatcher:
    """Tests for TitleMatcher."""

    def test_exact_match(self):
        """Exact title match should score 100."""
        from app.services.title_matcher import TitleMatcher
        matcher = TitleMatcher()
        result = matcher.compute(
            profile_titles=["Software Engineer"],
            job_title="Software Engineer",
        )
        assert result["score"] > 90

    def test_partial_match(self):
        """Partial title match should score between 0-100."""
        matcher = TitleMatcher()
        result = matcher.compute(
            profile_titles=["Frontend Developer"],
            job_title="Senior Frontend Engineer",
        )
        assert 0 < result["score"] < 100

    def test_no_match(self):
        """No title overlap should score low."""
        matcher = TitleMatcher()
        result = matcher.compute(
            profile_titles=["Nurse"],
            job_title="Software Engineer",
        )
        assert result["score"] < 50

    def test_multiple_titles_best(self):
        """Multiple titles should use the best match."""
        matcher = TitleMatcher()
        result = matcher.compute(
            profile_titles=["Junior Developer", "Senior Software Engineer"],
            job_title="Senior Software Engineer",
        )
        assert result["best_match_title"] == "Senior Software Engineer"
        assert result["score"] > 90


class TestMatchService:
    """Tests for the composite MatchService."""

    @pytest.mark.asyncio
    async def test_compute_score(self, sample_profile_data, sample_job_data):
        """Compute should return a complete score response."""
        from app.services.match_service import MatchService
        from app.schemas.match import MatchScoreRequest

        service = MatchService(db=AsyncMock())
        request = MatchScoreRequest(
            profile_id=1,
            job_id=1,
            profile_data=sample_profile_data,
            job_data=sample_job_data,
        )

        score = await service.compute_score(request)
        assert score.overall_score > 0

    @pytest.mark.asyncio
    async def test_compute_score_full(self, sample_profile_data, sample_job_data):
        """Full score computation should have all dimensions."""
        from app.services.match_service import MatchService
        from app.schemas.match import MatchScoreRequest

        service = MatchService(db=AsyncMock())
        request = MatchScoreRequest(
            profile_id=1,
            job_id=1,
            profile_data=sample_profile_data,
            job_data=sample_job_data,
        )

        score = await service.compute_score(request)
        assert score.overall_score > 0
        assert score.skills_score is not None
        assert score.experience_score is not None
        assert score.education_score is not None
        assert score.location_score is not None
        assert score.title_score is not None
        assert len(score.matched_skills) > 0
