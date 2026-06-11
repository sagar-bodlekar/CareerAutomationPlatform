"""Career Intelligence Agent - skill recommendations and interview prep."""

from typing import Any, Optional

from ..schemas.agents import AgentCapability
from .base_agent import AgentResult, BaseAgent


class CareerIntelligenceAgent(BaseAgent):
    """AI agent that provides career intelligence and growth recommendations."""

    @property
    def agent_id(self) -> str:
        return "career_intelligence"

    @property
    def name(self) -> str:
        return "Career Intelligence"

    @property
    def description(self) -> str:
        return "Career growth recommendations, skill suggestions, and interview preparation"

    @property
    def capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="skill_recommendation",
                description="Recommend skills to learn based on career goals",
                required_inputs=["current_skills", "target_role"],
            ),
            AgentCapability(
                name="interview_questions",
                description="Generate interview preparation questions",
                required_inputs=["job_title", "skills", "required_skills"],
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
        """Execute career intelligence based on capability requested."""
        capability = kwargs.get("capability", "skill_recommendation")

        template_map = {
            "skill_recommendation": "career_intelligence/skill_recommendation.j2",
            "interview_questions": "career_intelligence/interview_questions.j2",
        }

        template = template_map.get(capability)
        if not template:
            return AgentResult(success=False, content="", error=f"Unknown capability: {capability}")

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
