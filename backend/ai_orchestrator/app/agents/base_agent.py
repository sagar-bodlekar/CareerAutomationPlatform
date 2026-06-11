"""Base agent class for all AI agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from ..schemas.agents import AgentCapability, AgentDefinition, ExecuteResponse
from ..services.orchestrator import AIOrchestrator


@dataclass
class AgentResult:
    """Result from an agent execution."""

    success: bool
    content: str
    structured_data: Optional[dict] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    tokens_used: int = 0


class BaseAgent(ABC):
    """Abstract base class for AI agents.

    Each agent defines its capabilities, input/output schemas,
    and execution logic. Agents are registered in AGENT_REGISTRY.
    """

    def __init__(self, orchestrator: AIOrchestrator):
        self.orchestrator = orchestrator

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique agent identifier (e.g., 'resume_optimizer')."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """What this agent does."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> list[AgentCapability]:
        """List of capabilities this agent provides."""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default LLM model for this agent."""
        ...

    def get_definition(self) -> AgentDefinition:
        """Get the full agent definition."""
        return AgentDefinition(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            capabilities=self.capabilities,
            default_model=self.default_model,
            input_schema=self._get_input_schema(),
            output_schema=self._get_output_schema(),
        )

    def _get_input_schema(self) -> dict[str, Any]:
        """Return expected input fields as a dict schema."""
        return {}

    def _get_output_schema(self) -> dict[str, Any]:
        """Return expected output structure as a dict schema."""
        return {}

    @abstractmethod
    async def execute(
        self,
        inputs: dict[str, Any],
        **kwargs,
    ) -> AgentResult:
        """Execute the agent with given inputs."""
        ...

    async def execute_with_orchestrator(
        self,
        inputs: dict[str, Any],
        prompt_template: Optional[str] = None,
        system_prompt: Optional[str] = None,
        use_structured: bool = True,
    ) -> ExecuteResponse:
        """Execute using the AI Orchestrator.

        Uses the orchestrator's provider chain and logging.
        The prompt_template is forwarded to the orchestrator so it renders
        the correct capability-specific template (e.g., 'resume_optimizer/ats_optimization.j2').
        """
        from ..schemas.agents import ExecuteRequest

        request = ExecuteRequest(
            agent_id=self.agent_id,
            inputs=inputs,
            use_structured_output=use_structured,
        )

        return await self.orchestrator.execute(
            request=request,
            system_prompt=system_prompt,
            prompt_template=prompt_template,
        )
