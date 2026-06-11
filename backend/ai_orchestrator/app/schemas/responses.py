"""Usage and response schemas for AI orchestrator."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UsageStats(BaseModel):
    """Token usage and cost statistics."""

    total_executions: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    by_agent: dict[str, dict] = Field(default_factory=dict, description="Per-agent breakdown")


class AIAgentResponse(BaseModel):
    """Wrapper for AI agent response data."""

    content: str
    structured_data: Optional[dict] = None
    agent_name: str
    model_used: str
    tokens_used: int = 0
    duration_ms: int = 0
