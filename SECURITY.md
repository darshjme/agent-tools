# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please email the maintainers directly at: `security@example.com`

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive a response within 72 hours. We will coordinate disclosure with you.

## Scope

This library runs entirely in-process with no network calls. Key attack surfaces:

- **Schema injection**: malformed schema dicts passed to `SchemaValidator`
- **Timeout bypass**: `ToolCallGuard` uses daemon threads; ensure host process controls resources
- **Arbitrary execution**: `ToolRegistry.call` invokes registered callables — only register trusted functions

## Out of Scope

- Vulnerabilities in the Python standard library
- Denial-of-service via extremely large inputs (no hard limits are enforced by design)
