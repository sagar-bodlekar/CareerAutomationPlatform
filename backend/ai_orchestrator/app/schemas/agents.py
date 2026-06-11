"""AI agent and execution schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentCapability(BaseModel):
    """Description of an agent's capability."""

    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="What this capability does")
    required_inputs: list[str] = Field(default_factory=list, description="Required input field names")


class AgentDefinition(BaseModel):
    """Definition of a configured AI agent."""

    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="What this agent does")
    capabilities: list[AgentCapability] = Field(default_factory=list)
    default_model: str = Field("gemini-2.0-flash", description="Default LLM model")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="Expected input fields")
    output_schema: dict[str, Any] = Field(default_factory=dict, description="Expected output structure")
    is_active: bool = True


class ExecuteRequest(BaseModel):
    """Request to execute an AI task."""

    agent_id: str = Field(..., description="Agent to execute")
    prompt: Optional[str] = Field(None, description="Custom prompt override")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Input data for prompt templates")
    model: Optional[str] = Field(None, description="Model override")
    temperature: float = Field(0.2, ge=0.0, le=1.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Max output tokens")
    use_structured_output: bool = Field(True, description="Request JSON response format")
    user_id: Optional[int] = None
    profile_id: Optional[int] = None
    job_id: Optional[int] = None


class ExecuteResponse(BaseModel):
    """Response from an AI execution."""

    success: bool = True
    agent_id: str
    content: str
    structured: Optional[dict[str, Any]] = None
    model_used: str
    provider_used: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0
    fallback_used: bool = False
    error: Optional[str] = None
    execution_id: Optional[int] = None
