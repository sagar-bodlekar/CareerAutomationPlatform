"""Job Match Engine Agent - AI-enhanced job match scoring and analysis."""

from typing import Any, Optional

from ..schemas.agents import AgentCapability
from .base_agent import AgentResult, BaseAgent


class JobMatchEngineAgent(BaseAgent):
    """AI agent that enhances job matching with intelligent analysis."""

    @property
    def agent_id(self) -> str:
        return "job_match_engine"

    @property
    def name(self) -> str:
        return "Job Match Engine"

    @property
    def description(self) -> str:
        return "AI-enhanced job match scoring, skill gap analysis, and recommendations"

    @property
    def capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="match_scoring",
                description="Score a candidate's fit for a job using AI analysis",
                required_inputs=["skills", "experience_summary", "job_title", "required_skills"],
            ),
            AgentCapability(
                name="skill_gap_analysis",
                description="Analyze missing skills and provide learning recommendations",
                required_inputs=["current_skills", "required_skills", "experience_level"],
            ),
            AgentCapability(
                name="recommendation",
                description="Generate personalized match recommendations",
                required_inputs=["match_score", "job_title", "company_name", "strengths", "gaps"],
            ),
        ]

    @property
    def default_model(self) -> str:
        return "gemini-2.0-flash"

    async def execute(
        self,
        inputs: dict[str, Any],
        **kwargs,
    ) -> AgentResult:
        """Execute match engine based on capability requested."""
        capability = kwargs.get("capability", "match_scoring")

        template_map = {
            "match_scoring": "job_matcher/match_scoring.j2",
            "skill_gap_analysis": "job_matcher/skill_gap_analysis.j2",
            "recommendation": "job_matcher/recommendation.j2",
        }

        template = template_map.get(capability)
        if not template:
            return AgentResult(
                success=False,
                content="",
                error=f"Unknown capability: {capability}",
            )

        response = await self.execute_with_orchestrator(
            inputs=inputs,
            prompt_template=template,
            use_structured=True,
        )

        return AgentResult(
            success=response.success,
            content=response.content,
            structured_data=response.structured,
            error=response.error,
            execution_time_ms=response.duration_ms,
            tokens_used=response.total_tokens,
        )
