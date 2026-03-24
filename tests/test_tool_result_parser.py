"""Tests for ToolResultParser."""

import pytest

from agent_tools import ToolResultParser


@pytest.fixture
def parser():
    return ToolResultParser()


# ── parse_json ─────────────────────────────────────────────────────────────────

def test_plain_json(parser):
    result = parser.parse_json('{"key": "value"}')
    assert result == {"key": "value"}


def test_json_fenced_block(parser):
    text = '```json\n{"answer": 42}\n```'
    result = parser.parse_json(text)
    assert result == {"answer": 42}


def test_json_fenced_block_no_lang(parser):
    text = '```\n{"x": 1}\n```'
    result = parser.parse_json(text)
    assert result == {"x": 1}


def test_trailing_comma(parser):
    result = parser.parse_json('{"a": 1, "b": 2,}')
    assert result["b"] == 2


def test_single_quotes(parser):
    result = parser.parse_json("{'name': 'Alice', 'age': 30}")
    assert result == {"name": "Alice", "age": 30}


def test_nested_json(parser):
    result = parser.parse_json('{"user": {"id": 1, "tags": ["a", "b"]}}')
    assert result["user"]["tags"] == ["a", "b"]


def test_invalid_json_raises(parser):
    with pytest.raises(ValueError, match="Could not parse JSON"):
        parser.parse_json("not json at all !!!")


def test_non_string_raises(parser):
    with pytest.raises(ValueError, match="Expected str"):
        parser.parse_json(123)  # type: ignore


def test_json_array_raises(parser):
    """Top-level array is not a dict — should raise."""
    with pytest.raises(ValueError, match="not a dict"):
        parser.parse_json("[1, 2, 3]")


# ── parse_tool_call ────────────────────────────────────────────────────────────

def test_parse_tool_call_from_dict(parser):
    raw = {"tool_name": "search", "arguments": {"query": "hello"}}
    result = parser.parse_tool_call(raw)
    assert result["tool_name"] == "search"
    assert result["arguments"]["query"] == "hello"


def test_parse_tool_call_from_string(parser):
    raw = '{"tool_name": "search", "arguments": {"query": "hello"}}'
    result = parser.parse_tool_call(raw)
    assert result["tool_name"] == "search"


def test_parse_tool_call_openai_style(parser):
    raw = {
        "function_call": {
            "name": "get_weather",
            "arguments": '{"city": "Paris"}',
        }
    }
    result = parser.parse_tool_call(raw)
    assert result["tool_name"] == "get_weather"
    assert result["arguments"]["city"] == "Paris"


def test_parse_tool_call_anthropic_style(parser):
    raw = {
        "type": "tool_use",
        "name": "web_search",
        "input": {"query": "cats"},
    }
    result = parser.parse_tool_call(raw)
    assert result["tool_name"] == "web_search"
    assert result["arguments"]["query"] == "cats"


def test_parse_tool_call_invalid_type_raises(parser):
    with pytest.raises(ValueError, match="Expected str or dict"):
        parser.parse_tool_call(42)  # type: ignore


# ── is_error_response ──────────────────────────────────────────────────────────

def test_is_error_status(parser):
    assert parser.is_error_response({"status": "error"}) is True


def test_is_error_status_failed(parser):
    assert parser.is_error_response({"status": "failed"}) is True


def test_is_ok_status(parser):
    assert parser.is_error_response({"status": "ok", "result": "data"}) is False


def test_is_error_success_false(parser):
    assert parser.is_error_response({"success": False, "message": "oops"}) is True


def test_is_error_ok_false(parser):
    assert parser.is_error_response({"ok": False}) is True


def test_is_error_error_key_present(parser):
    assert parser.is_error_response({"error": "something went wrong"}) is True


def test_is_error_error_key_none(parser):
    assert parser.is_error_response({"error": None, "result": "ok"}) is False


def test_is_error_non_dict(parser):
    assert parser.is_error_response("not a dict") is False  # type: ignore
