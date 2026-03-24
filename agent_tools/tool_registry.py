"""ToolRegistry — register, validate, and call tools for LLM agents."""

from __future__ import annotations

from typing import Any, Callable

from .exceptions import (
    ToolExecutionError,
    ToolInputError,
    ToolNotFoundError,
    ToolOutputError,
    ValidationError,
)
from .schema_validator import SchemaValidator


class _ToolEntry:
    __slots__ = ("name", "func", "input_schema", "output_schema")

    def __init__(
        self,
        name: str,
        func: Callable,
        input_schema: dict,
        output_schema: dict | None,
    ):
        self.name = name
        self.func = func
        self.input_schema = input_schema
        self.output_schema = output_schema


class ToolRegistry:
    """
    Central registry for LLM agent tools.

    Example::

        registry = ToolRegistry()

        def add(a: int, b: int) -> dict:
            return {"sum": a + b}

        registry.register(
            "add",
            add,
            input_schema={"a": {"type": "int", "required": True},
                          "b": {"type": "int", "required": True}},
            output_schema={"sum": {"type": "int"}},
        )

        result = registry.call("add", a=1, b=2)
        # {"sum": 3}
    """

    def __init__(self) -> None:
        self._tools: dict[str, _ToolEntry] = {}
        self._validator = SchemaValidator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        func: Callable,
        input_schema: dict,
        output_schema: dict | None = None,
    ) -> None:
        """
        Register a tool.

        Args:
            name:          Unique tool name.
            func:          Callable to invoke.
            input_schema:  Schema for keyword arguments passed to func.
            output_schema: Optional schema for the dict returned by func.

        Raises:
            ValueError: If name is empty or func is not callable.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Tool name must be a non-empty string.")
        if not callable(func):
            raise ValueError(f"func must be callable, got {type(func).__name__}.")
        if not isinstance(input_schema, dict):
            raise ValueError("input_schema must be a dict.")

        self._tools[name] = _ToolEntry(
            name=name,
            func=func,
            input_schema=input_schema,
            output_schema=output_schema,
        )

    def call(self, name: str, **kwargs: Any) -> dict:
        """
        Validate inputs, call the tool, validate output, and return the result.

        Args:
            name:    Registered tool name.
            **kwargs: Arguments forwarded to the tool function.

        Returns:
            The dict returned by the tool function.

        Raises:
            ToolNotFoundError:   Tool not in registry.
            ToolInputError:      Input fails input_schema validation.
            ToolOutputError:     Output fails output_schema validation.
            ToolExecutionError:  Tool raised an unexpected exception.
        """
        entry = self._get_entry(name)

        # --- validate inputs ---
        try:
            self._validator.validate(kwargs, entry.input_schema)
        except ValidationError as exc:
            raise ToolInputError(name, exc) from exc

        # --- execute ---
        try:
            result = entry.func(**kwargs)
        except Exception as exc:
            raise ToolExecutionError(name, exc) from exc

        # --- validate output ---
        if entry.output_schema is not None:
            if not isinstance(result, dict):
                err = ValidationError(
                    f"Tool must return a dict, got {type(result).__name__}."
                )
                raise ToolOutputError(name, err)
            try:
                self._validator.validate(result, entry.output_schema)
            except ValidationError as exc:
                raise ToolOutputError(name, exc) from exc

        return result

    def list_tools(self) -> list[str]:
        """Return sorted list of registered tool names."""
        return sorted(self._tools.keys())

    def get_schema(self, name: str) -> dict:
        """
        Return the schema info for a registered tool.

        Returns:
            {"input_schema": {...}, "output_schema": {...} | None}

        Raises:
            ToolNotFoundError: If tool is not registered.
        """
        entry = self._get_entry(name)
        return {
            "input_schema": entry.input_schema,
            "output_schema": entry.output_schema,
        }

    def unregister(self, name: str) -> None:
        """Remove a tool from the registry."""
        if name not in self._tools:
            raise ToolNotFoundError(name)
        del self._tools[name]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_entry(self, name: str) -> _ToolEntry:
        entry = self._tools.get(name)
        if entry is None:
            raise ToolNotFoundError(name)
        return entry
