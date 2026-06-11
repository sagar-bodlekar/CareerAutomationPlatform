"""Test fixtures for AI orchestrator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.providers.base import LLMResponse
from app.services.prompt_engine import PromptEngine
from app.services.response_parser import ResponseParser


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    return LLMResponse(
        content='{"score": 85, "recommendation": "Strong match"}',
        model_name="gemini-2.0-flash",
        provider="gemini",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        duration_ms=500,
    )


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator."""
    orchestrator = AsyncMock()
    orchestrator.execute = AsyncMock()
    return orchestrator


@pytest.fixture
def prompt_engine():
    """Create a real prompt engine."""
    return PromptEngine()


@pytest.fixture
def response_parser():
    """Create a real response parser."""
    return ResponseParser()
