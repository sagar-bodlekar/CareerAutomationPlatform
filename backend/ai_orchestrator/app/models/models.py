"""AI Orchestrator models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from shared.database import Base


class AIExecutionLog(Base):
    """Log of AI execution for audit, cost tracking, and debugging."""

    __tablename__ = "ai_execution_logs"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False, index=True, comment="Name of the agent (e.g., resume_optimizer)")
    model_provider = Column(String(50), nullable=False, comment="gemini or groq")
    model_name = Column(String(100), nullable=False, comment="e.g., gemini-2.0-flash")
    prompt_template = Column(String(255), nullable=True, comment="Path to prompt template used")
    input_tokens = Column(Integer, nullable=True, comment="Prompt tokens")
    output_tokens = Column(Integer, nullable=True, comment="Completion tokens")
    total_tokens = Column(Integer, nullable=True, comment="Total tokens consumed")
    cost_estimate = Column(Float, nullable=True, comment="Estimated cost in USD")
    duration_ms = Column(Integer, nullable=True, comment="Execution duration in milliseconds")
    success = Column(Integer, default=1, nullable=False, comment="Whether execution succeeded")
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    retry_count = Column(Integer, default=0, nullable=False)
    provider_fallback_used = Column(Integer, default=0, comment="Whether fallback provider was used")
    input_preview = Column(String(500), nullable=True, comment="Preview of input (truncated)")
    output_preview = Column(String(500), nullable=True, comment="Preview of output (truncated)")
    raw_request = Column(JSONB, nullable=True, comment="Full request payload (stripped of sensitive data)")
    raw_response = Column(JSONB, nullable=True, comment="Full response payload")
    user_id = Column(Integer, nullable=True, comment="Associated user (if applicable)")
    profile_id = Column(Integer, nullable=True, comment="Associated profile (if applicable)")
    job_id = Column(Integer, nullable=True, comment="Associated job (if applicable)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
