"""ATS Optimizer — orchestrates analysis, scoring, and optimization."""

from app.services.ats.analyzer import ATSAnalyzer
from app.services.ats.recommendation_engine import ATSRecommendationEngine
from app.services.ats.scorer import ATSScorer


class ATSOptimizer:
    """Orchestrates ATS analysis, scoring, and content optimization."""

    def __init__(self) -> None:
        self.analyzer = ATSAnalyzer()
        self.scorer = ATSScorer()
        self.recommendation_engine = ATSRecommendationEngine()

    async def analyze_and_optimize(
        self,
        resume_content: dict,
        job_description: str,
    ) -> dict:
        """Run full ATS analysis on a resume for a given job.

        Args:
            resume_content: Structured resume content dict.
            job_description: Target job description text.

        Returns:
            Dict with ``score``, ``score_breakdown``, ``recommendations``,
            ``missing_keywords``, ``matched_keywords``, and optional
            ``optimized_content``.
        """
        # Analyze resume content
        resume_analysis = self.analyzer.analyze_resume_content(resume_content)
        job_analysis = self.analyzer.analyze_job_description(job_description)

        # Compute scores
        score_result = self.scorer.score(
            resume_skills=resume_analysis["skills"],
            resume_sections=resume_analysis["sections_present"],
            resume_years=resume_analysis["experience_years"],
            job_description=job_description,
        )

        # Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            score_breakdown=score_result,
            resume_content=resume_content,
            job_description=job_description,
        )

        return {
            "score": score_result["overall_score"],
            "score_breakdown": {
                "keyword_score": score_result["keyword_score"],
                "section_score": score_result["section_score"],
                "experience_score": score_result["experience_score"],
                "skills_score": score_result["skills_score"],
            },
            "recommendations": recommendations,
            "missing_keywords": score_result["missing_keywords"],
            "matched_keywords": score_result["matched_keywords"],
        }

    async def optimize_content(
        self,
        resume_content: dict,
        job_description: str,
    ) -> dict:
        """Optimize resume content for ATS compatibility.

        Returns analysis results. Full AI-powered content optimization
        will be connected in Phase 6 (AI Orchestrator).

        Args:
            resume_content: Structured resume content dict.
            job_description: Target job description text.

        Returns:
            Same as ``analyze_and_optimize`` plus optimized content stub.
        """
        result = await self.analyze_and_optimize(resume_content, job_description)

        # Stub: Phase 6 will integrate AI content optimization here
        result["optimized_content"] = None
        result["optimization_pending"] = True
        result["message"] = (
            "AI-powered content optimization will be available in a future update. "
            "For now, use the recommendations above to manually improve your resume."
        )

        return result
