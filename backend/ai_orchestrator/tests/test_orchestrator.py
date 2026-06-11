"""Tests for AI orchestrator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.agents import ExecuteRequest


class TestAIOrchestrator:
    """Tests for AIOrchestrator."""

    @pytest.mark.asyncio
    async def test_execute_no_providers(self):
        """Execute should fail gracefully when no providers configured."""
        with patch("app.services.orchestrator.app_settings.gemini_api_key", None), \
             patch("app.services.orchestrator.app_settings.groq_api_key", None):

            from app.services.orchestrator import AIOrchestrator
            orchestrator = AIOrchestrator()

            request = ExecuteRequest(agent_id="test", inputs={})
            response = await orchestrator.execute(request)
            assert response.success is False
            assert "No AI providers" in (response.error or "")

    @pytest.mark.asyncio
    async def test_execute_with_gemini(self):
        """Execute should use Gemini provider when available."""
        from app.services.orchestrator import AIOrchestrator

        orchestrator = AIOrchestrator()

        # Mock providers
        mock_provider = AsyncMock()
        mock_provider.provider_name = "gemini"
        mock_provider.default_model = "gemini-2.0-flash"

        from app.providers.base import LLMResponse
        mock_response = LLMResponse(
            content='{"score": 85}',
            model_name="gemini-2.0-flash",
            provider="gemini",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            duration_ms=500,
        )
        mock_provider.generate_structured = AsyncMock(return_value=mock_response)

        orchestrator._providers = [mock_provider]

        request = ExecuteRequest(agent_id="test_agent", inputs={})
        response = await orchestrator.execute(request)
        assert response.success is True
        assert response.provider_used == "gemini"
        assert response.total_tokens == 150

    @pytest.mark.asyncio
    async def test_execute_fallback(self):
        """Execute should fall back to Groq when Gemini fails."""
        from app.services.orchestrator import AIOrchestrator

        orchestrator = AIOrchestrator()

        # Mock Gemini provider (fails)
        gemini = AsyncMock()
        gemini.provider_name = "gemini"
        from app.providers.base import ProviderError
        gemini.generate_structured = AsyncMock(
            side_effect=ProviderError("Rate limited", "gemini", recoverable=True)
        )

        # Mock Groq provider (succeeds)
        groq = AsyncMock()
        groq.provider_name = "groq"
        from app.providers.base import LLMResponse
        groq_response = LLMResponse(
            content='{"score": 72}',
            model_name="llama-3.3-70b-versatile",
            provider="groq",
            input_tokens=80,
            output_tokens=40,
            total_tokens=120,
            duration_ms=600,
        )
        groq.generate_structured = AsyncMock(return_value=groq_response)

        orchestrator._providers = [gemini, groq]

        request = ExecuteRequest(agent_id="test_agent", inputs={})
        response = await orchestrator.execute(request)
        assert response.success is True
        assert response.fallback_used is True
        assert response.provider_used == "groq"

    @pytest.mark.asyncio
    async def test_execute_all_providers_fail(self):
        """Execute should return error when all providers fail."""
        from app.services.orchestrator import AIOrchestrator

        orchestrator = AIOrchestrator()

        gemini = AsyncMock()
        gemini.provider_name = "gemini"
        from app.providers.base import ProviderError
        gemini.generate_structured = AsyncMock(
            side_effect=ProviderError("Error", "gemini", recoverable=True)
        )

        groq = AsyncMock()
        groq.provider_name = "groq"
        groq.generate_structured = AsyncMock(
            side_effect=ProviderError("Error", "groq", recoverable=True)
        )

        orchestrator._providers = [gemini, groq]

        request = ExecuteRequest(agent_id="test_agent", inputs={})
        response = await orchestrator.execute(request)
        assert response.success is False
        assert response.error is not None

    def test_estimate_cost_known_model(self):
        """Cost estimation should work for known models."""
        from app.services.orchestrator import AIOrchestrator
        orchestrator = AIOrchestrator()

        cost = orchestrator._estimate_cost("gemini-2.0-flash", 1000, 500)
        assert cost > 0
        assert cost < 1.0  # Should be a small fraction of a cent
