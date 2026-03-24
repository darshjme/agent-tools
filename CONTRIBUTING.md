# Contributing to agent-tools

Thank you for taking the time to contribute!

## Development Setup

```bash
git clone https://github.com/example/agent-tools
cd agent-tools
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests must pass before submitting a PR.

## Code Style

- Follow PEP 8
- Use type hints on all public APIs
- Keep zero runtime dependencies (stdlib only)

## Pull Request Guidelines

1. Fork the repo and create a feature branch from `main`
2. Write tests for your change — no test, no merge
3. Update `CHANGELOG.md` under `[Unreleased]`
4. Run the full test suite locally
5. Open a PR with a clear description of what and why

## Reporting Bugs

Open an issue with:
- Python version and OS
- Minimal reproducible example
- Full traceback

## Security Issues

Please **do not** open public issues for security vulnerabilities.
See [SECURITY.md](SECURITY.md) instead.
