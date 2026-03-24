"""ToolResultParser — extract structured data from LLM tool call responses."""

from __future__ import annotations

import json
import re
from typing import Any


class ToolResultParser:
    """
    Parse and normalize LLM tool call responses.

    Handles:
    - Fenced code blocks (```json ... ```)
    - Trailing commas in JSON
    - Single-quoted JSON (common in Python-generated strings)
    - Raw dicts passed through unchanged
    - Detects error responses by multiple conventions
    """

    # Patterns that indicate an error response
    _ERROR_STATUS_VALUES = {"error", "failed", "failure", "err"}
    _ERROR_KEYS = {"error", "err", "exception", "traceback", "message"}

    def parse_json(self, text: str) -> dict:
        """
        Parse a JSON string into a dict.

        Handles:
        - Optional ````json` or ```` fenced code blocks
        - Trailing commas before ``}`` or ``]``
        - Single-quoted strings (converted to double-quoted)

        Args:
            text: Raw text potentially containing JSON.

        Returns:
            Parsed dict.

        Raises:
            ValueError: If the text cannot be parsed as JSON.
        """
        if not isinstance(text, str):
            raise ValueError(f"Expected str, got {type(text).__name__}.")

        cleaned = text.strip()

        # 1. Strip fenced code blocks
        fence_match = re.search(
            r"```(?:json)?\s*([\s\S]*?)```", cleaned, re.IGNORECASE
        )
        if fence_match:
            cleaned = fence_match.group(1).strip()

        # 2. Remove trailing commas before } or ]
        cleaned = re.sub(r",\s*([\}\]])", r"\1", cleaned)

        # 3. Try standard JSON first
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            # 4. Convert single quotes to double quotes (naive but effective for simple cases)
            try:
                single_to_double = self._single_to_double_quotes(cleaned)
                result = json.loads(single_to_double)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Could not parse JSON from text: {text[:200]!r}"
                ) from exc

        if not isinstance(result, dict):
            raise ValueError(
                f"Parsed JSON is not a dict (got {type(result).__name__})."
            )
        return result

    def parse_tool_call(self, raw: str | dict) -> dict:
        """
        Normalize a raw tool call into a standard dict.

        Accepts:
        - A raw JSON string (parsed via parse_json)
        - A dict (returned as-is with light normalization)

        Normalizes keys:
        - ``tool_use`` / ``function_call`` → ``tool_name`` + ``arguments``
        - Ensures ``tool_name`` and ``arguments`` keys are present

        Args:
            raw: Raw tool call (string or dict).

        Returns:
            Normalized dict with at least ``{"tool_name": str, "arguments": dict}``.

        Raises:
            ValueError: If the input cannot be normalized.
        """
        if isinstance(raw, str):
            data = self.parse_json(raw)
        elif isinstance(raw, dict):
            data = dict(raw)  # shallow copy
        else:
            raise ValueError(f"Expected str or dict, got {type(raw).__name__}.")

        # Normalize OpenAI-style function_call
        if "function_call" in data and "tool_name" not in data:
            fc = data["function_call"]
            data["tool_name"] = fc.get("name", "")
            args = fc.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            data["arguments"] = args

        # Normalize Anthropic-style tool_use block
        if "type" in data and data.get("type") == "tool_use":
            data.setdefault("tool_name", data.get("name", ""))
            data.setdefault("arguments", data.get("input", {}))

        # Ensure minimum keys
        data.setdefault("tool_name", data.get("name", ""))
        data.setdefault("arguments", data.get("parameters", data.get("args", {})))

        return data

    def is_error_response(self, result: dict) -> bool:
        """
        Return True if *result* looks like an error response.

        Checks:
        - ``result["status"]`` in error status values
        - ``result["error"]`` is truthy (non-None, non-empty)
        - ``result["success"]`` is explicitly False
        - ``result["ok"]`` is explicitly False
        - Top-level key ``"error"`` or ``"exception"`` present and truthy

        Args:
            result: The result dict to inspect.

        Returns:
            bool
        """
        if not isinstance(result, dict):
            return False

        status = result.get("status")
        if isinstance(status, str) and status.lower() in self._ERROR_STATUS_VALUES:
            return True

        if result.get("success") is False:
            return True

        if result.get("ok") is False:
            return True

        for key in ("error", "err", "exception"):
            val = result.get(key)
            if val is not None and val not in (False, "", 0):
                return True

        return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _single_to_double_quotes(text: str) -> str:
        """
        Naively convert single-quoted JSON to double-quoted.

        Only handles simple cases — properly escaped strings in valid JSON.
        """
        # Replace single-quoted strings: 'value' → "value"
        # Strategy: use a regex to find quoted regions and swap delimiter
        result = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == "'":
                # Consume single-quoted string
                result.append('"')
                i += 1
                while i < len(text):
                    c = text[i]
                    if c == "\\":
                        # Pass through escape sequence
                        result.append(c)
                        i += 1
                        if i < len(text):
                            result.append(text[i])
                            i += 1
                    elif c == "'":
                        result.append('"')
                        i += 1
                        break
                    elif c == '"':
                        # Escape double quotes inside single-quoted string
                        result.append('\\"')
                        i += 1
                    else:
                        result.append(c)
                        i += 1
            elif ch == '"':
                # Pass through double-quoted string as-is
                result.append(ch)
                i += 1
                while i < len(text):
                    c = text[i]
                    result.append(c)
                    if c == "\\":
                        i += 1
                        if i < len(text):
                            result.append(text[i])
                            i += 1
                    elif c == '"':
                        i += 1
                        break
                    else:
                        i += 1
            else:
                result.append(ch)
                i += 1
        return "".join(result)
