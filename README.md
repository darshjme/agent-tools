# agent-tools

> **Zero-dependency Python library for tool call validation and schema enforcement in LLM agents.**

Catches silent failures, schema mismatches, and type errors *before* they poison your agent's context window.

---

## The Problem

LLM agents call tools. Tools fail silently. Bad outputs slip into context. The agent hallucinates a fix. The loop spirals.

`agent-tools` adds a validation layer between your agent and its tools:

```
Agent → [ToolCallGuard] → [ToolRegistry] → Tool → [SchemaValidator] → Agent
```

Every call is validated on the way in and out. Errors are normalized into structured dicts. Timeouts and retries are handled automatically.

---

## Installation

```bash
pip install agent-tools
```

Requires Python ≥ 3.10. **Zero runtime dependencies.**

---

## Components

### 1. SchemaValidator

Validates any dict against a lightweight schema — no `jsonschema` needed.

```python
from agent_tools import SchemaValidator, ValidationError

validator = SchemaValidator()

schema = {
    "query":  {"type": "str",  "required": True},
    "limit":  {"type": "int",  "required": False},
    "mode":   {"type": "str",  "enum": ["fast", "slow"]},
    "tags":   {"type": "list", "items": {"type": "str"}},
}

validator.validate({"query": "cats", "limit": 10, "mode": "fast"}, schema)
# ✅ passes

try:
    validator.validate({"query": 42}, schema)
except ValidationError as e:
    print(e)  # [query] Expected str, got int.
```

**Supported types:** `str`, `int`, `float`, `bool`, `list`, `dict`, `any`  
**Field options:** `required`, `enum`, `items` (list element schema), `properties` (nested dict schema)

---

### 2. ToolRegistry

Register tools with schemas. Validates inputs before calling, outputs after.

```python
from agent_tools import ToolRegistry, ToolNotFoundError, ToolInputError

registry = ToolRegistry()

def web_search(query: str, limit: int = 5) -> dict:
    # ... real implementation
    return {"results": ["result1", "result2"], "total": 2}

registry.register(
    "web_search",
    web_search,
    input_schema={
        "query": {"type": "str", "required": True},
        "limit": {"type": "int"},
    },
    output_schema={
        "results": {"type": "list", "required": True},
        "total":   {"type": "int",  "required": True},
    },
)

result = registry.call("web_search", query="agent frameworks", limit=3)
print(result)  # {"results": [...], "total": 2}

print(registry.list_tools())   # ["web_search"]
print(registry.get_schema("web_search"))  # {"input_schema": {...}, "output_schema": {...}}
```

**Exceptions raised:**
- `ToolNotFoundError` — tool not registered
- `ToolInputError` — input fails schema
- `ToolOutputError` — output fails schema
- `ToolExecutionError` — tool raised an exception

---

### 3. ToolCallGuard

Retry + timeout + error normalization. Always returns a structured dict.

```python
from agent_tools import ToolCallGuard, ToolTimeoutError

guard = ToolCallGuard(max_retries=2, timeout_seconds=10.0)

def flaky_api(city: str) -> dict:
    # might fail
    return {"temp": 22, "unit": "C"}

result = guard.call(flaky_api, city="Mumbai")
print(result)
# {"status": "ok", "result": {"temp": 22, "unit": "C"}, "error": None, "attempts": 1}

# On repeated failure:
# {"status": "error", "result": None, "error": "Connection refused", "attempts": 3}
```

**Raises `ToolTimeoutError`** if the call exceeds `timeout_seconds`.

---

### 4. ToolResultParser

Parse messy LLM outputs into clean dicts.

```python
from agent_tools import ToolResultParser

parser = ToolResultParser()

# Fenced code blocks
parser.parse_json('```json\n{"answer": 42}\n```')
# → {"answer": 42}

# Trailing commas
parser.parse_json('{"a": 1, "b": 2,}')
# → {"a": 1, "b": 2}

# Single quotes (Python-style)
parser.parse_json("{'name': 'Alice'}")
# → {"name": "Alice"}

# Normalize OpenAI function_call format
parser.parse_tool_call({
    "function_call": {"name": "search", "arguments": '{"q": "cats"}'}
})
# → {"tool_name": "search", "arguments": {"q": "cats"}, ...}

# Detect errors
parser.is_error_response({"status": "error", "error": "timeout"})  # True
parser.is_error_response({"status": "ok", "result": "data"})       # False
```

---

## Full Example: Agent Tool Loop

```python
from agent_tools import ToolRegistry, ToolCallGuard, ToolResultParser

registry = ToolRegistry()
guard = ToolCallGuard(max_retries=2, timeout_seconds=15.0)
parser = ToolResultParser()

def get_weather(city: str) -> dict:
    return {"temp": 28, "condition": "sunny"}

registry.register(
    "get_weather",
    get_weather,
    input_schema={"city": {"type": "str", "required": True}},
    output_schema={
        "temp":      {"type": "float", "required": True},
        "condition": {"type": "str",   "required": True},
    },
)

# Simulate LLM tool call response
raw_llm_output = '```json\n{"tool_name": "get_weather", "arguments": {"city": "Delhi"}}\n```'
tool_call = parser.parse_tool_call(raw_llm_output)

# Execute with guard
result = guard.call(
    registry.call,
    name=tool_call["tool_name"],
    **tool_call["arguments"],
)

if parser.is_error_response(result):
    print(f"Tool failed: {result['error']}")
else:
    print(f"Weather: {result['result']}")
```

---

## License

MIT © 2026 agent-tools contributors
