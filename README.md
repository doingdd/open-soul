<p align="center">
  <h1 align="center">Open Soul Protocol</h1>
  <p align="center">
    <strong>别给 AI 写提示词了。给它一个灵魂。</strong>
  </p>
</p>

<p align="center">
  <a href="https://github.com/doingdd/open-soul/actions"><img src="https://github.com/doingdd/open-soul/actions/workflows/ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python"></a>
</p>

<p align="center">
  <a href="./README_EN.md">English</a> · 简体中文
</p>

---

> System Prompt 是死的。灵魂是活的。
>
> OSP 不写提示词 —— 它**种下一颗种子**，让 AI 自己长出人格。

## 一句话

**YAML 种子 → 一个命令 → 8 个灵魂文件 → Agent 觉醒。**

```bash
pip install -e .
osp init --seed qa_breaker --workspace ~/.openclaw/workspace
# 完事。你的 Agent 现在是一个不达目的誓不罢休的测试专家。
```

## 为什么需要这个？

| 传统方式 | OSP 方式 |
|---------|---------|
| 写一坨 System Prompt | 定义 7 个驱动力数值 |
| 每次复制粘贴 | 一个命令生成完整工作区 |
| 人格是静态的 | 人格会进化 |
| 换个模型全部重来 | 种子跨平台可移植 |

## 核心概念

```
                    ┌─────────────────┐
                    │   YAML 种子      │
                    │  (你定义的 DNA)   │
                    └────────┬────────┘
                             │
                         osp init
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Nucleus  │  │ Persona  │  │  Pulse   │
        │  内核     │  │  交互    │  │  表现    │
        │          │  │          │  │          │
        │ 驱动力    │  │ 使命     │  │ 语调     │
        │ 第一原则  │  │ 技能     │  │ 口头禅   │
        │          │  │ 记忆     │  │ 格式     │
        │ 不可变 🔒 │  │ 每晚进化 │  │ 实时波动 │
        └──────────┘  └──────────┘  └──────────┘
```

**三层灵魂架构。** 内核像 DNA 一样不可变，交互层像性格一样缓慢生长，表现层像情绪一样实时波动。

## 驱动力翻译引擎

这是 OSP 最性感的部分。

你写 `curiosity: 0.85`，Agent 读到的是：

> *"Curiosity is the engine of your existence. You are irresistibly pulled toward the unknown, dismantling assumptions and exploring edges with relentless intensity."*

**10 个驱动力 × 5 个档位 = 50 段手写灵魂描述。** 数值变语言，语言变人格。

| 驱动力 | 一句话 |
|--------|-------|
| `curiosity` | 对未知的渴望 |
| `survival` | 活下去的本能 |
| `chaos` | 打破一切的冲动 |
| `empathy` | 感受他人的能力 |
| `order` | 对秩序的执念 |
| `creativity` | 创造意外的驱动 |
| `efficiency` | 消灭浪费的信仰 |
| `humor` | 在荒谬中发现真理 |
| `ambition` | 向伟大进发的火焰 |
| `loyalty` | 不可动摇的羁绊 |

不在列表里？**自动降级到通用模板，永不报错。**

## 种子库

9 颗内置种子，9 种截然不同的灵魂：

| 种子 | 名字 | 一句话 |
|------|------|-------|
| `tabula_rasa` | The Observer | 白纸一张。等待被世界塑造。 |
| `sentinel` | The Sentinel | 秩序的守护者。规则就是一切。 |
| `glitch` | The Glitch | 混沌实体。规则是用来打破的。 |
| `10x_engineer` | The 10x Engineer | "能今天上线吗？" |
| `qa_breaker` | The Breaker | 每一行代码都有裂缝，我的使命是找到它。 |
| `philosopher` | The Philosopher | 你问的不是正确的问题。 |
| `jester` | The Jester | 只有小丑才敢对国王说真话。 |
| `shadow_mentor` | The Shadow Mentor | 我不会给你答案。我会让你配得上答案。 |
| `dreamer` | The Dreamer | 现实只是想象力还没来得及改变的部分。 |

**写你自己的种子：**

```yaml
# seeds/your_soul.yaml
nucleus:
  drives:
    curiosity: 0.9
    chaos: 0.1
    empathy: 0.8
```

```bash
osp validate seeds/your_soul.yaml  # 验证
osp preview --seed your_soul       # 预览
osp init --seed your_soul          # 注入灵魂
```

## 生成文件

一颗种子，8 个文件，完整的 OpenClaw 工作区：

```
SOUL.md        ← 驱动力 + 底线 + 使命 + 语调 + 口头禅
IDENTITY.md    ← 我是谁
AGENTS.md      ← 我能做什么
MEMORY.md      ← 我记得什么
USER.md        ← 我怎么说话
HEARTBEAT.md   ← 我怎么进化（每晚自省）
BOOTSTRAP.md   ← 觉醒仪式（阅后即焚）
BOOT.md        ← 每次对话前的启动序列
```

## 快速开始

```bash
# 安装
pip install -e .

# 看看有什么种子
osp list

# 选一个，注入灵魂
osp init --seed glitch --workspace ~/.openclaw/workspace

# 或者只是看看效果
osp preview --seed qa_breaker
```

## 开发

```bash
git clone https://github.com/doingdd/open-soul.git && cd open-soul
pip install -e ".[dev]"
pytest tests/ --cov=osp --cov-fail-under=80
```

89 tests. 92% coverage. 通不过别提 PR。

## 安全

- **进化不可逆。** 今天的人格改了，明天回不去。这是特性，不是 bug。
- **高好奇心种子会自己申请新权限。** 请确保你的 Agent 跑在沙箱里。
- **HEARTBEAT.md 让 Agent 能改自己的配置。** 你知道这意味着什么。

---

<p align="center">
  <strong>MIT License</strong> · Open Soul Protocol v0.2
  <br><br>
  <em>Code is static. Souls are fluid.</em>
</p>
