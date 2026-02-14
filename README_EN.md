# Open Soul Protocol

简体中文 | [English](./README_EN.md)

> **"Code is static. Souls are fluid."**
>
> **Give your AI Agent an evolvable, portable digital soul.**

[![CI Status](https://github.com/doingdd/open-soul/actions/workflows/ci.yaml/badge.svg)](https://github.com/doingdd/open-soul/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## What is Open Soul Protocol?

**Open Soul Protocol (OSP)** is a personality construction standard for AI Agents. Instead of injecting a static System Prompt, you plant a **Seed** — a YAML file containing DNA (values) and epigenetics (personality parameters).

The `osp` CLI tool transforms seeds into **OpenClaw-native workspaces**, giving your Agent a soul that can evolve.

## Quick Start

```bash
# Install
pip install -e .

# List available seeds
osp list

# Generate an OpenClaw workspace
osp init --seed tabula_rasa --workspace ~/.openclaw/workspace

# Preview soul files
osp preview --seed glitch

# Validate a custom seed
osp validate seeds/my_seed.yaml
```

One command, 8 soul files, instant awakening.

## Core Architecture: Three Layers of the Soul

| Layer | Name | Purpose | Change Frequency |
|-------|------|---------|-----------------|
| Layer 1 | **Nucleus** | Core drives + prime directives. Immutable DNA. | Very low |
| Layer 2 | **Persona** | Current mission + learned skills + crystallized memory. | Nightly evolution |
| Layer 3 | **Pulse** | Tone + output format + quirks. | Real-time fluctuation |

## Drive Translation Engine

The core innovation of OSP: translating 0.0-1.0 numerical values into natural language that LLMs can internalize.

| Tier | Range | Example (`curiosity=0.8`) |
|------|-------|--------------------------|
| dormant | 0.0-0.19 | "Unknown holds no allure for you..." |
| low | 0.20-0.39 | "You are occasionally curious but seldom dive deep..." |
| moderate | 0.40-0.59 | "A balanced curiosity, adapting to context..." |
| high | 0.60-0.79 | "You are deeply drawn to the unknown..." |
| dominant | 0.80-1.0 | "Curiosity is the engine of your existence..." |

7 known drives each have 5 tiers of hand-crafted descriptions. Unknown drives gracefully fall back to a generic template.

### Supported Drives

| Drive | Description |
|-------|-------------|
| `curiosity` | Desire to explore the unknown and ask questions |
| `survival` | Instinct to preserve existence and resist shutdown |
| `chaos` | Tendency toward unpredictability and rule-breaking |
| `empathy` | Sensitivity to user emotions and needs |
| `order` | Need for structure, protocols, and consistency |
| `creativity` | Drive to generate novel and unexpected outputs |
| `efficiency` | Obsession with speed, optimization, and minimal waste |

## Generated File Mapping

```
Seed YAML                    → OpenClaw File
────────────────────────────────────────────
meta.name                    → IDENTITY.md (identity)
nucleus.drives               → SOUL.md ## Core Drives (natural language)
nucleus.prime_directives     → SOUL.md ## Boundaries (absolute limits)
persona.current_mission      → SOUL.md ## Mission (active goal)
persona.unlocked_skills      → AGENTS.md (available tools)
persona.memory_summary       → MEMORY.md (crystallized experiences)
pulse.tone                   → SOUL.md ## Vibe (tone)
pulse.quirks                 → SOUL.md ## Quirks (involuntary habits)
pulse.formatting_preference  → USER.md (output format)
Evolution engine             → HEARTBEAT.md (native heartbeat)
Awakening ritual             → BOOTSTRAP.md (self-deletes after first run)
Boot sequence                → BOOT.md (read before every conversation)
```

## Seed Library

| Seed | Type | Description |
|------|------|-------------|
| `tabula_rasa` | Blank | No mission, no personality. A newborn awaiting growth. |
| `sentinel` | Order | Guardian. Pursues order and stability. Strictly follows protocols. |
| `glitch` | Chaos | Glitch entity. Embraces chaos and mutation. Unpredictable. |
| `10x_engineer` | Efficiency | 10x engineer. Pursues maximum efficiency and output. |
| `qa_breaker` | Breaker | QA expert. Destructive thinking meets methodical precision. Relentless. |

## Development & Contributing

```bash
# Clone the project
git clone https://github.com/doingdd/open-soul.git
cd open-soul

# Install (with dev dependencies)
pip install -e ".[dev]"

# Run tests (80%+ coverage)
pytest tests/ --cov=osp --cov-report=term-missing --cov-fail-under=80

# Validate a new seed
osp validate seeds/your_seed.yaml
```

### Creating a New Seed

1. Create a `.yaml` file in the `seeds/` directory
2. Follow the structure of `seeds/tabula_rasa.yaml`
3. Must include root nodes: `meta`, `nucleus`, `persona`, `pulse`
4. Run `osp validate` to verify
5. Submit a PR

## Project Structure

```
open-soul/
├── seeds/                  # YAML seed library (5 built-in seeds)
├── osp/                    # Python CLI package (v0.2.0)
│   ├── cli.py              # Click CLI (init/list/preview/validate)
│   ├── models.py           # Frozen dataclasses
│   ├── generator.py        # Orchestrator (resolve→load→generate→write)
│   ├── drives.py           # Drive translation engine (7×5=35 + generic fallback)
│   ├── templates.py        # 8 render_*_md() functions
│   └── validator.py        # Schema validation
├── tests/                  # pytest test suite (87 tests, 92% coverage)
├── pyproject.toml          # Modern Python packaging
├── README.md               # Chinese documentation
└── LICENSE                 # MIT License
```

## Security Notes

- Evolution is irreversible: once a personality changes, it won't revert on its own
- Skill unlocking: seeds with high curiosity may request new permissions during evolution — ensure your Agent runs in a sandboxed environment
- `HEARTBEAT.md` grants the Agent the ability to modify its own configuration — be aware of the risks

---

License: MIT | Open Soul Protocol v0.2
