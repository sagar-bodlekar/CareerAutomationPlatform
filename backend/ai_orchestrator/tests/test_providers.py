"""Tests for LLM providers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.providers.base import LLMProvider, LLMResponse, ProviderError


class TestLLMBase:
    """Tests for the LLMProvider base class."""

    def test_llm_response_defaults(self):
        """LLMResponse should have sensible defaults."""
        response = LLMResponse(
            content="Hello",
            model_name="test-model",
            provider="test",
        )
        assert response.content == "Hello"
        assert response.input_tokens == 0
        assert response.output_tokens == 0
        assert response.total_tokens == 0

    def test_provider_error(self):
        """ProviderError should format correctly."""
        error = ProviderError("API error", "gemini", recoverable=True)
        assert str(error) == "[gemini] API error"
        assert error.recoverable is True
        assert error.provider == "gemini"


class TestGeminiProvider:
    """Tests for Gemini provider (with mocked client)."""

    @pytest.mark.asyncio
    async def test_generate_success(self, mock_llm_response):
        """Generate should return LLMResponse on success."""
        with patch("app.providers.gemini.GeminiProvider._get_client") as mock_client:
            mock_gen = AsyncMock()
            mock_response = MagicMock()
            mock_response.text = '{"score": 85}'
            mock_response.usage_metadata = MagicMock(
                prompt_token_count=100,
                candidates_token_count=50,
                total_token_count=150,
            )
            mock_gen.return_value = mock_response
            mock_client.return_value.aio.models.generate_content = mock_gen

            from app.providers.gemini import GeminiProvider
            provider = GeminiProvider()
            response = await provider.generate("Hello")
            assert response.content == '{"score": 85}'
            assert response.provider == "gemini"
            assert response.total_tokens == 150

    @pytest.mark.asyncio
    async def test_generate_api_key_error(self):
        """Generate should raise ProviderError on missing API key."""
        with patch("app.providers.gemini.GeminiProvider._get_client") as mock_client:
            mock_client.side_effect = ProviderError("API_KEY required", "gemini", recoverable=False)

            from app.providers.gemini import GeminiProvider
            provider = GeminiProvider()
            with pytest.raises(ProviderError):
                await provider.generate("Hello")


class TestResponseParser:
    """Tests for ResponseParser."""

    def test_extract_json_from_code_block(self):
        """Should extract JSON from markdown code blocks."""
        parser = ResponseParser()
        text = '```json\n{"key": "value"}\n```'
        result = parser.extract_json(text)
        assert result == '{"key": "value"}'

    def test_extract_json_from_text(self):
        """Should extract JSON from plain text."""
        parser = ResponseParser()
        text = 'Here is the result: {"score": 85, "match": "good"}'
        result = parser.extract_json(text)
        assert "score" in result

    def test_extract_json_no_json(self):
        """Should return None when no JSON found."""
        parser = ResponseParser()
        result = parser.extract_json("This is just plain text with no JSON")
        assert result is None

    def test_clean_json_trailing_commas(self):
        """Should remove trailing commas."""
        parser = ResponseParser()
        cleaned = parser.clean_json('{"skills": ["a", "b",], "score": 85,}')
        assert ",]" not in cleaned
        assert ",}" not in cleaned

    def test_parse_valid_json(self):
        """Should parse valid JSON string."""
        parser = ResponseParser()
        result = parser.parse('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_with_schema(self):
        """Should validate against Pydantic schema."""
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str
            score: int

        parser = ResponseParser()
        result = parser.parse('{"name": "test", "score": 85}', schema=TestSchema)
        assert result["name"] == "test"
        assert result["score"] == 85

    def test_parse_fails_validation(self):
        """Should raise ValueError on schema validation failure."""
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str

        parser = ResponseParser()
        with pytest.raises(ValueError, match="Schema validation failed"):
            parser.parse('{"wrong_field": 123}', schema=TestSchema)
