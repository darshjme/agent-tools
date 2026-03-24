"""Custom exceptions for agent-tools."""


class AgentToolsError(Exception):
    """Base exception for all agent-tools errors."""


class ToolNotFoundError(AgentToolsError):
    """Raised when a requested tool is not registered."""

    def __init__(self, name: str):
        self.tool_name = name
        super().__init__(f"Tool '{name}' is not registered.")


class ValidationError(AgentToolsError):
    """Raised when data fails schema validation."""

    def __init__(self, message: str, field_path: str = ""):
        self.field_path = field_path
        super().__init__(f"[{field_path}] {message}" if field_path else message)


class ToolInputError(AgentToolsError):
    """Raised when tool input fails schema validation."""

    def __init__(self, tool_name: str, cause: ValidationError):
        self.tool_name = tool_name
        self.cause = cause
        super().__init__(f"Input validation failed for tool '{tool_name}': {cause}")


class ToolOutputError(AgentToolsError):
    """Raised when tool output fails schema validation."""

    def __init__(self, tool_name: str, cause: ValidationError):
        self.tool_name = tool_name
        self.cause = cause
        super().__init__(f"Output validation failed for tool '{tool_name}': {cause}")


class ToolExecutionError(AgentToolsError):
    """Raised when tool execution raises an unexpected exception."""

    def __init__(self, tool_name: str, cause: Exception):
        self.tool_name = tool_name
        self.cause = cause
        super().__init__(f"Execution error in tool '{tool_name}': {cause}")


class ToolTimeoutError(AgentToolsError):
    """Raised when a tool call exceeds the configured timeout."""

    def __init__(self, timeout_seconds: float):
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Tool call timed out after {timeout_seconds}s.")
