"""ToolCallGuard — retry, timeout, and error normalization for tool calls."""

from __future__ import annotations

import threading
import time
from typing import Any, Callable

from .exceptions import ToolTimeoutError


class ToolCallGuard:
    """
    Wraps any callable with:
    - Configurable retry on exception
    - Per-call timeout via a background thread
    - Normalized return envelope

    Example::

        guard = ToolCallGuard(max_retries=2, timeout_seconds=5.0)

        def risky_tool(query: str) -> dict:
            return {"answer": "42"}

        result = guard.call(risky_tool, query="what is life?")
        # {"status": "ok", "result": {"answer": "42"}, "error": None, "attempts": 1}
    """

    def __init__(
        self,
        max_retries: int = 2,
        timeout_seconds: float = 30.0,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0.")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0.")

        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def call(self, func: Callable, **kwargs: Any) -> dict:
        """
        Call *func* with **kwargs**, applying retry + timeout logic.

        Returns:
            ``{"status": "ok"|"error", "result": Any, "error": str|None, "attempts": int}``

        Raises:
            ToolTimeoutError: If the call does not complete within timeout_seconds.
        """
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 2):  # +2: initial + retries
            result_container: dict[str, Any] = {}
            exc_container: list[Exception] = []

            def _run() -> None:
                try:
                    result_container["value"] = func(**kwargs)
                except Exception as e:  # noqa: BLE001
                    exc_container.append(e)

            thread = threading.Thread(target=_run, daemon=True)
            thread.start()
            thread.join(timeout=self.timeout_seconds)

            if thread.is_alive():
                # Thread is still running — timeout exceeded
                raise ToolTimeoutError(self.timeout_seconds)

            if exc_container:
                last_exc = exc_container[0]
                continue  # retry

            # Success
            return {
                "status": "ok",
                "result": result_container.get("value"),
                "error": None,
                "attempts": attempt,
            }

        # All attempts exhausted
        return {
            "status": "error",
            "result": None,
            "error": str(last_exc),
            "attempts": self.max_retries + 1,
        }
