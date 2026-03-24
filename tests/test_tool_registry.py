"""Tests for ToolRegistry."""

import pytest

from agent_tools import (
    ToolRegistry,
    ToolNotFoundError,
    ToolInputError,
    ToolOutputError,
    ToolExecutionError,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_registry():
    reg = ToolRegistry()
    reg.register(
        "add",
        lambda a, b: {"sum": a + b},
        input_schema={
            "a": {"type": "int", "required": True},
            "b": {"type": "int", "required": True},
        },
        output_schema={"sum": {"type": "int"}},
    )
    return reg


# ── register / list / get_schema ──────────────────────────────────────────────

def test_register_and_list():
    reg = make_registry()
    assert "add" in reg.list_tools()


def test_list_sorted():
    reg = ToolRegistry()
    reg.register("z_tool", lambda: {}, input_schema={})
    reg.register("a_tool", lambda: {}, input_schema={})
    assert reg.list_tools() == ["a_tool", "z_tool"]


def test_get_schema():
    reg = make_registry()
    schema = reg.get_schema("add")
    assert "input_schema" in schema
    assert "output_schema" in schema


def test_get_schema_not_found():
    reg = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        reg.get_schema("missing")


def test_register_invalid_name():
    reg = ToolRegistry()
    with pytest.raises(ValueError):
        reg.register("", lambda: {}, input_schema={})


def test_register_not_callable():
    reg = ToolRegistry()
    with pytest.raises(ValueError):
        reg.register("bad", "not_callable", input_schema={})  # type: ignore


# ── call — happy path ─────────────────────────────────────────────────────────

def test_call_success():
    reg = make_registry()
    result = reg.call("add", a=2, b=3)
    assert result == {"sum": 5}


def test_call_no_output_schema():
    reg = ToolRegistry()
    reg.register(
        "echo",
        lambda msg: {"echo": msg},
        input_schema={"msg": {"type": "str", "required": True}},
    )
    result = reg.call("echo", msg="hello")
    assert result["echo"] == "hello"


# ── call — error cases ─────────────────────────────────────────────────────────

def test_call_not_found():
    reg = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        reg.call("nope")


def test_call_input_error():
    reg = make_registry()
    with pytest.raises(ToolInputError):
        reg.call("add", a="not_int", b=1)


def test_call_missing_required_input():
    reg = make_registry()
    with pytest.raises(ToolInputError):
        reg.call("add", a=1)  # b is missing


def test_call_execution_error():
    reg = ToolRegistry()
    def boom(x):
        raise RuntimeError("kaboom")
    reg.register("boom", boom, input_schema={"x": {"type": "int", "required": True}})
    with pytest.raises(ToolExecutionError, match="kaboom"):
        reg.call("boom", x=1)


def test_call_output_error():
    reg = ToolRegistry()
    reg.register(
        "badout",
        lambda x: {"result": "string_not_int"},
        input_schema={"x": {"type": "int", "required": True}},
        output_schema={"result": {"type": "int"}},
    )
    with pytest.raises(ToolOutputError):
        reg.call("badout", x=1)


def test_call_output_not_dict():
    reg = ToolRegistry()
    reg.register(
        "returns_list",
        lambda x: [1, 2, 3],
        input_schema={"x": {"type": "int", "required": True}},
        output_schema={"items": {"type": "list"}},
    )
    with pytest.raises(ToolOutputError, match="must return a dict"):
        reg.call("returns_list", x=1)


# ── unregister ────────────────────────────────────────────────────────────────

def test_unregister():
    reg = make_registry()
    reg.unregister("add")
    assert "add" not in reg.list_tools()


def test_unregister_not_found():
    reg = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        reg.unregister("ghost")
