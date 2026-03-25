<div align="center">

<img src="assets/agent-tools-hero.png" alt="agent-tools — Vedic Arsenal by Darshankumar Joshi" width="100%" />

# 🪷 agent-tools

<h3><em>शस्त्र</em></h3>

> *Shastra — sacred tools wielded with precision*

**Tool call validation and schema enforcement for LLM agents — silent failure detection, retry logic, result parsing. Zero dependencies.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen?style=flat-square)](https://github.com/darshjme/agent-tools)
[![Tests](https://img.shields.io/badge/Tests-Passing-success?style=flat-square)](https://github.com/darshjme/agent-tools/actions)
[![License](https://img.shields.io/badge/License-MIT-pink?style=flat-square)](LICENSE)
[![Vedic Arsenal](https://img.shields.io/badge/Vedic%20Arsenal-100%20libs-purple?style=flat-square)](https://github.com/darshjme/arsenal)

*Part of the [**Vedic Arsenal**](https://github.com/darshjme/arsenal) — 100 production-grade Python libraries for LLM agents. Zero dependencies. Battle-tested.*

</div>

---

## Overview

`agent-tools` implements **tool call validation and schema enforcement for llm agents — silent failure detection, retry logic, result parsing. zero dependencies.**

Inspired by the Vedic principle of *शस्त्र* (Shastra), this library brings the ancient wisdom of structured discipline to modern LLM agent engineering.

No external dependencies. Pure Python 3.8+. Drop it in anywhere.

## Installation

```bash
pip install agent-tools
```

Or clone directly:
```bash
git clone https://github.com/darshjme/agent-tools.git
cd agent-tools
pip install -e .
```

## How It Works

```mermaid
flowchart LR
    A[Input] --> B[agent-tools]
    B --> C{Process}
    C -- Success --> D[Output]
    C -- Error --> E[Handle / Retry]
    E --> B
    style B fill:#6b21a8,color:#fff
    note["Tools — Zero Dependencies"]
```

## Quick Start

```python
from tools import *

# Initialize
# See examples/ for full usage patterns
```

## Why `agent-tools`?

Production LLM systems fail in predictable ways. `agent-tools` solves the **tools** failure mode with:

- **Zero dependencies** — no version conflicts, no bloat
- **Battle-tested patterns** — extracted from real production systems
- **Type-safe** — full type hints, mypy-compatible
- **Minimal surface area** — one job, done well
- **Composable** — works with any LLM framework (LangChain, LlamaIndex, raw OpenAI, etc.)

## The Vedic Arsenal

`agent-tools` is part of **[darshjme/arsenal](https://github.com/darshjme/arsenal)** — a collection of 100 focused Python libraries for LLM agent infrastructure.

Each library solves exactly one problem. Together they form a complete stack.

```
pip install agent-tools  # this library
# Browse all 100: https://github.com/darshjme/arsenal
```

## Contributing

Found a bug? Have an improvement?

1. Fork the repo
2. Create a feature branch (`git checkout -b fix/your-fix`)
3. Add tests
4. Open a PR

All contributions welcome. Keep it zero-dependency.

## License

MIT — use freely, build freely.

---

<div align="center">

**Built with 🪷 by [Darshankumar Joshi](https://github.com/darshjme)** · [@thedarshanjoshi](https://twitter.com/thedarshanjoshi)

*"कर्मण्येवाधिकारस्ते मा फलेषु कदाचन"*
*Your right is to action alone, never to the fruits thereof.*

[Arsenal](https://github.com/darshjme/arsenal) · [GitHub](https://github.com/darshjme) · [Twitter](https://twitter.com/thedarshanjoshi)

</div>
