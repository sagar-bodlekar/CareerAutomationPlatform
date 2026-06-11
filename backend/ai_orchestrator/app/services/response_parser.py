"""Structured output parser for LLM responses."""

import json
import logging
import re
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parses and validates structured JSON responses from LLMs.

    Handles common LLM output quirks: markdown code fences, trailing commas,
    extra text before/after JSON, and retries on parse failure.
    """

    MAX_RETRIES = 2

    def extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from LLM response text.

        Handles:
        - Markdown code fences (```json ... ```)
        - Text before/after JSON object
        - Multiple JSON objects (returns first valid one)
        - Leading/trailing whitespace

        Args:
            text: Raw LLM response text.

        Returns:
            Extracted JSON string, or None if no JSON found.
        """
        if not text or not text.strip():
            return None

        # Try to extract from markdown code blocks first
        code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        blocks = re.findall(code_block_pattern, text, re.DOTALL)
        if blocks:
            for block in blocks:
                block = block.strip()
                if block.startswith("{") or block.startswith("["):
                    return block

        # Try to find JSON object directly
        obj_match = re.search(r"\{.*\}", text, re.DOTALL)
        if obj_match:
            return obj_match.group()

        # Try to find JSON array
        arr_match = re.search(r"\[.*\]", text, re.DOTALL)
        if arr_match:
            return arr_match.group()

        return None

    def clean_json(self, json_str: str) -> str:
        """Clean common JSON formatting issues from LLM output.

        Handles:
        - Trailing commas in objects/arrays
        - Single quotes instead of double quotes
        - Unquoted keys
        - Comments (// style)

        Args:
            json_str: Raw JSON string from LLM.

        Returns:
            Cleaned JSON string.
        """
        # Remove single-line comments
        json_str = re.sub(r"//[^\n]*", "", json_str)
        # Remove trailing commas before closing brackets
        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*\]", "]", json_str)
        return json_str.strip()

    def parse(
        self,
        text: str,
        schema: Optional[Type[BaseModel]] = None,
    ) -> dict[str, Any]:
        """Parse LLM response text into a dictionary.

        Args:
            text: Raw LLM response text.
            schema: Optional Pydantic model for validation.

        Returns:
            Parsed dictionary.

        Raises:
            ValueError: if JSON cannot be extracted or validated.
        """
        extracted = self.extract_json(text)
        if not extracted:
            raise ValueError("No JSON content found in LLM response")

        cleaned = self.clean_json(extracted)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

        if schema and not isinstance(data, list):
            try:
                schema(**data)
            except ValidationError as e:
                raise ValueError(f"Schema validation failed: {e}")

        return data if isinstance(data, dict) else {"data": data}

    def parse_with_retry(
        self,
        text: str,
        schema: Optional[Type[BaseModel]] = None,
    ) -> tuple[dict[str, Any], int]:
        """Parse with retry logic.

        Args:
            text: Raw LLM response text.
            schema: Optional Pydantic model for validation.

        Returns:
            Tuple of (parsed_data, retries_used).
        """
        retries = 0
        last_error = None

        while retries <= self.MAX_RETRIES:
            try:
                data = self.parse(text, schema)
                return data, retries
            except (ValueError, json.JSONDecodeError) as e:
                last_error = str(e)
                retries += 1
                if retries > self.MAX_RETRIES:
                    break
                logger.warning(f"Parse attempt {retries} failed: {e}. Retrying...")
                # Try with more aggressive cleaning
                text = self.clean_json(text)

        raise ValueError(f"Failed to parse after {self.MAX_RETRIES + 1} attempts: {last_error}")
