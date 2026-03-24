"""Tests for ToolCallGuard."""

import time

import pytest

from agent_tools import ToolCallGuard, ToolTimeoutError


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_success():
    guard = ToolCallGuard()
    result = guard.call(lambda x: {"v": x}, x=42)
    assert result["status"] == "ok"
    assert result["result"] == {"v": 42}
    assert result["error"] is None
    assert result["attempts"] == 1


def test_attempts_increments_on_retry():
    calls = []
    def flaky(x):
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("not yet")
        return {"v": x}

    guard = ToolCallGuard(max_retries=2)
    result = guard.call(flaky, x=7)
    assert result["status"] == "ok"
    assert result["attempts"] == 2


def test_all_retries_exhausted():
    guard = ToolCallGuard(max_retries=1)
    def always_fail():
        raise RuntimeError("always bad")
    result = guard.call(always_fail)
    assert result["status"] == "error"
    assert "always bad" in result["error"]
    assert result["attempts"] == 2  # initial + 1 retry


def test_zero_retries():
    guard = ToolCallGuard(max_retries=0)
    def fail():
        raise ValueError("fail")
    result = guard.call(fail)
    assert result["status"] == "error"
    assert result["attempts"] == 1


# ── Timeout ────────────────────────────────────────────────────────────────────

def test_timeout_raises():
    guard = ToolCallGuard(max_retries=0, timeout_seconds=0.2)
    def slow():
        time.sleep(5)
        return {"done": True}
    with pytest.raises(ToolTimeoutError):
        guard.call(slow)


def test_fast_call_no_timeout():
    guard = ToolCallGuard(max_retries=0, timeout_seconds=2.0)
    result = guard.call(lambda: {"ok": True})
    assert result["status"] == "ok"


# ── Config validation ──────────────────────────────────────────────────────────

def test_negative_retries_raises():
    with pytest.raises(ValueError):
        ToolCallGuard(max_retries=-1)


def test_zero_timeout_raises():
    with pytest.raises(ValueError):
        ToolCallGuard(timeout_seconds=0)
