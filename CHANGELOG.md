# Changelog

All notable changes to **agent-tools** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.1.0] — 2026-03-24

### Added
- **ToolRegistry** — register tools with input/output schemas; validates before and after execution
- **SchemaValidator** — zero-dependency JSON Schema-like dict validator; supports type, required, enum, nested list items, nested dict properties
- **ToolCallGuard** — wraps callables with retry, timeout (threading.Timer), and normalized result envelope
- **ToolResultParser** — parses LLM tool call responses: fenced code blocks, trailing commas, single quotes, OpenAI & Anthropic normalization, error detection
- Custom exception hierarchy: `AgentToolsError`, `ToolNotFoundError`, `ToolInputError`, `ToolOutputError`, `ToolExecutionError`, `ToolTimeoutError`, `ValidationError`
- 20+ pytest tests with 100% pass rate
- Zero runtime dependencies (Python ≥ 3.10 stdlib only)
