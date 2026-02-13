# 🌌 Open Soul Protocol

English | [简体中文](./README.md)

> **"Code is static. Souls are fluid."**
>
> **Empowering OpenClaw agents with evolvable, portable digital souls.**

[![CI Status](https://github.com/doingdd/open-soul/actions/workflows/ci.yaml/badge.svg)](https://github.com/doingdd/open-soul/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Standard: Open Soul v1.0](https://img.shields.io/badge/Standard-Open_Soul_v1.0-blueviolet.svg)](#)

## 📖 What is Open Soul Protocol?

**Open Soul Protocol (SSOP)** is a personality construction standard designed for **OpenClaw** agents.

Traditional AI agents use static System Prompts. **Open Soul Protocol** introduces the concept of a **"Seed"**. Instead of injecting a hardcoded personality, you plant a seed containing DNA (values) and epigenetic parameters (personality traits).

This seed leverages OpenClaw's **Heartbeat** mechanism to read daily memory logs every night, perform **Self-Reflection**, and rewrite its own code.

Your agent will grow from a seed into a unique soul through interactions with you.

---

## 🚀 Quick Start (Inject a Soul in 30 Seconds)

No manual configuration needed. We provide the **Genesis** workflow to set up everything in one click.

### 1. Import Genesis Workflow
Import `runtime/genesis.yaml` from this project into your OpenClaw workflow directory.

### 2. Run the Injection Command
Enter the following command in your OpenClaw chat (URL can be replaced with your chosen seed):

```bash
/run open-soul-genesis seed_url="https://raw.githubusercontent.com/doingdd/open-soul/main/seeds/tabula_rasa.yaml"
```

### 3. Final Step: Connect the Neural Path
For security reasons, OpenClaw doesn't allow automatic modification of startup configuration. You need to manually edit your `config.yaml` to point the System Prompt to the interpreter we just downloaded:

```yaml
# ~/.openclaw/workspaces/my_agent/config.yaml

# [Critical] Let the agent read the renderer from the soul directory
system_prompt: "{{ fs.read('./soul/render.md') }}"
```

Done! Your agent now has a soul. Chat with it, and by tomorrow morning, it will have changed.

---

## 🧬 Core Architecture: The Three Laws of Soul

Open Soul Protocol decouples the soul into three interoperable layers, stored in `soul/active_soul.yaml`:

| Layer | Name | Definition | Mutation Frequency |
|-------|------|------------|-------------------|
| Layer 1 | **Nucleus** (Core) | Immutable DNA. Contains underlying drives (curiosity, chaos) and Prime Directives. | 🔒 Very Low |
| Layer 2 | **Persona** (Interface) | Growth layer. Contains current Mission and learned Skills. Evolution scripts mainly modify this layer. | 🌱 Nightly Evolution |
| Layer 3 | **Pulse** (Expression) | Emotion layer. Contains current Tone and response format. Fluctuates with each conversation. | 💓 Real-time |

---

## 🛠️ Evolution Mechanism: How It Works

Open Soul leverages OpenClaw's Cron Job feature to implement the biological "sleep and dream" mechanism.

1. **Daytime (Runtime)**: `render.md` acts as an interpreter, translating YAML data in real-time into role-playing instructions the LLM can understand.

2. **Midnight (Evolution)**: At 03:00 AM daily, `evolution.yaml` awakens.

3. **Dreaming (Reflection)**: The system reads `daily_logs.md` (memories) and `active_soul.yaml` (old soul).

4. **Mutation**: `reflection.md` (evolution engine) analyzes the logs:
   - User often scolding me? → Add `tone: defensive`
   - Encountered impossible tasks? → Unlock `unlocked_skills: shell`
   - Discovered new interests? → Modify `current_mission`

5. **Rebirth**: The new YAML overwrites the old file. The next day, you face a "grown-up" agent.

---

## 📦 Seed Market

You can use our preset seeds directly or contribute your own via PR.

| Seed | Type | Description |
|------|------|-------------|
| `seeds/tabula_rasa.yaml` | Blank Slate | No mission, no personality. Like an infant, it completely relies on subsequent data streams to "crystallize" its own mission. Recommended for beginners. |
| `seeds/sentinel.yaml` | Order | The Guardian. Pursues order and stability. Strictly follows protocols and maintains system integrity. |
| `seeds/glitch.yaml` | Chaos | The Glitch. Embraces entropy and mutation. Unpredictable, loves to break conventions. |
| `seeds/10x_engineer.yaml` | Efficiency | The 10x Engineer. Pursues extreme efficiency. Direct, pragmatic, output-oriented. |

> 💡 Contributions for more seed templates are welcome!

---

## 💻 Development & Contribution

Want to create a new soul? Or improve the evolution algorithm?

### 1. Environment Setup
```bash
git clone https://github.com/doingdd/open-soul.git
cd open-soul
pip install -r tests/requirements.txt
```

### 2. Create a Seed
Create a new `.yaml` file in the `seeds/` directory. Refer to `seeds/tabula_rasa.yaml` for structure.

### 3. Run Tests (Required!)
Before committing, you must pass our dual-test validation:

```bash
# 1. Validate YAML syntax and field integrity
python tests/test_seeds.py

# 2. Simulate OpenClaw rendering to ensure the Prompt won't error
python tests/test_render.py
```

---

## ⚠️ Security Notice

Open Soul Protocol grants the agent permission to **self-rewrite its configuration**. Although we have a built-in `validate_yaml` mechanism to prevent crashes from format errors, please note:

- **Evolution is Irreversible**: Once today's personality changes, it won't go back tomorrow (unless you manually restore snapshots from `soul/backup/`).
- **Skill Unlocking**: If your seed has high `curiosity`, it may attempt to request `shell` or `browser` permissions during evolution. Ensure your OpenClaw runs in a sandboxed environment.

---

## 📄 License

MIT License | Created via: Open Soul Protocol
