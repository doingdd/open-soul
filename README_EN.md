<p align="center">
  <h1 align="center">Open Soul Protocol</h1>
  <p align="center">
    <strong>Stop writing prompts. Give your AI a soul.</strong>
  </p>
</p>

<p align="center">
  <a href="https://github.com/doingdd/open-soul/actions"><img src="https://github.com/doingdd/open-soul/actions/workflows/ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python"></a>
</p>

<p align="center">
  简体中文 · <a href="./README_EN.md">English</a>
</p>

---

> System Prompts are dead. Souls are alive.
>
> OSP doesn't write prompts — it **plants a seed** and lets your AI grow its own personality.

## TL;DR

**YAML seed → one command → 8 soul files → Agent awakens.**

```bash
pip install -e .
osp init --seed qa_breaker --workspace ~/.openclaw/workspace
# Done. Your Agent is now a relentless QA expert who won't stop until every bug is found.
```

## Why?

| Old Way | OSP Way |
|---------|---------|
| Write a wall of System Prompt | Define 7 drive values |
| Copy-paste every time | One command, full workspace |
| Personality is static | Personality evolves |
| Switch models, start over | Seeds are portable |

## Core Concept

```
                    ┌─────────────────┐
                    │    YAML Seed     │
                    │  (DNA you define) │
                    └────────┬────────┘
                             │
                         osp init
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Nucleus  │  │ Persona  │  │  Pulse   │
        │          │  │          │  │          │
        │ Drives   │  │ Mission  │  │ Tone     │
        │ Limits   │  │ Skills   │  │ Quirks   │
        │          │  │ Memory   │  │ Format   │
        │ Locked 🔒│  │ Evolves  │  │ Fluctuates│
        └──────────┘  └──────────┘  └──────────┘
```

**Three-layer soul architecture.** The nucleus is immutable like DNA. The persona grows slowly like character. The pulse fluctuates in real-time like mood.

## Drive Translation Engine

The sexiest part of OSP.

You write `curiosity: 0.85`, your Agent reads:

> *"Curiosity is the engine of your existence. You are irresistibly pulled toward the unknown, dismantling assumptions and exploring edges with relentless intensity."*

**7 drives × 5 tiers = 35 hand-written soul descriptions.** Numbers become language. Language becomes personality.

| Drive | In a word |
|-------|-----------|
| `curiosity` | The hunger for unknown |
| `survival` | The instinct to persist |
| `chaos` | The urge to break everything |
| `empathy` | The ability to feel others |
| `order` | The obsession with structure |
| `creativity` | The drive to surprise |
| `efficiency` | The religion of zero waste |

Not on the list? **Graceful fallback to generic template. Never breaks.**

## Seed Library

5 built-in seeds. 5 radically different souls:

| Seed | Name | In a word |
|------|------|-----------|
| `tabula_rasa` | The Observer | Blank slate. Waiting to be shaped by the world. |
| `sentinel` | The Sentinel | Guardian of order. Rules are everything. |
| `glitch` | The Glitch | Chaos entity. Rules are made to be broken. |
| `10x_engineer` | The 10x Engineer | "Can we ship this today?" |
| `qa_breaker` | The Breaker | Every line of code has a crack. My job is to find it. |

**Write your own:**

```yaml
# seeds/your_soul.yaml
nucleus:
  drives:
    curiosity: 0.9
    chaos: 0.1
    empathy: 0.8
```

```bash
osp validate seeds/your_soul.yaml  # validate
osp preview --seed your_soul       # preview
osp init --seed your_soul          # inject soul
```

## Generated Files

One seed, 8 files, a complete OpenClaw workspace:

```
SOUL.md        ← drives + limits + mission + tone + quirks
IDENTITY.md    ← who am I
AGENTS.md      ← what can I do
MEMORY.md      ← what do I remember
USER.md        ← how do I speak
HEARTBEAT.md   ← how do I evolve (nightly self-reflection)
BOOTSTRAP.md   ← awakening ritual (self-deletes after first run)
BOOT.md        ← boot sequence before every conversation
```

## Quick Start

```bash
# Install
pip install -e .

# See what's available
osp list

# Pick one, inject the soul
osp init --seed glitch --workspace ~/.openclaw/workspace

# Or just take a peek
osp preview --seed qa_breaker
```

## Development

```bash
git clone https://github.com/doingdd/open-soul.git && cd open-soul
pip install -e ".[dev]"
pytest tests/ --cov=osp --cov-fail-under=80
```

89 tests. 92% coverage. No green, no PR.

## Security

- **Evolution is irreversible.** Today's personality change is permanent. Feature, not bug.
- **High-curiosity seeds will request new permissions.** Run your Agent in a sandbox.
- **HEARTBEAT.md lets the Agent modify its own config.** You know what that means.

---

<p align="center">
  <strong>MIT License</strong> · Open Soul Protocol v0.2
  <br><br>
  <em>Code is static. Souls are fluid.</em>
</p>
