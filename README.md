# Open Soul Protocol

[English](./README_EN.md) | 简体中文

> **"Code is static. Souls are fluid."**
>
> **为 AI Agent 赋予可进化、可移植的数字灵魂。**

[![CI Status](https://github.com/doingdd/open-soul/actions/workflows/ci.yaml/badge.svg)](https://github.com/doingdd/open-soul/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 什么是 Open Soul Protocol?

**Open Soul Protocol (OSP)** 是一个 AI Agent 人格构建标准。你注入的不是一个写死的 System Prompt，而是一颗**种子 (Seed)** —— 包含 DNA（价值观）、表观遗传学（性格参数）的 YAML 文件。

`osp` CLI 工具能将种子转化为 **OpenClaw 原生工作区**，让 Agent 立即拥有可进化的灵魂。

## 快速开始

```bash
# 安装
pip install -e .

# 查看可用种子
osp list

# 生成 OpenClaw 工作区
osp init --seed tabula_rasa --workspace ~/.openclaw/workspace

# 预览灵魂文件
osp preview --seed glitch

# 验证自定义种子
osp validate seeds/my_seed.yaml
```

一个命令，8 个灵魂文件，Agent 瞬间觉醒。

## 核心架构：灵魂三层

| 层级 | 名称 | 作用 | 变更频率 |
|------|------|------|---------|
| Layer 1 | **Nucleus** (内核) | 底层驱动力 + 第一原则。不可变的 DNA。 | 极低 |
| Layer 2 | **Persona** (交互) | 当前使命 + 已习得技能 + 记忆结晶。 | 每晚进化 |
| Layer 3 | **Pulse** (表现) | 语调 + 回复格式 + 口头禅。 | 实时波动 |

## 驱动力翻译引擎

OSP 的核心创新：将 0.0-1.0 的数值翻译为 LLM 能内化的自然语言。

| 档位 | 范围 | 示例 (`curiosity=0.8`) |
|------|------|----------------------|
| dormant | 0.0-0.19 | "未知对你毫无吸引力..." |
| low | 0.20-0.39 | "你偶尔好奇但很少深入..." |
| moderate | 0.40-0.59 | "平衡的好奇心，随场景而动..." |
| high | 0.60-0.79 | "你被未知深深吸引..." |
| dominant | 0.80-1.0 | "好奇心是你存在的引擎..." |

7 个已知驱动力各有 5 档手工撰写的描述，未知驱动力自动降级到通用模板。

### 支持的驱动力

| 驱动力 | 描述 |
|--------|------|
| `curiosity` | 探索未知和提问的欲望 |
| `survival` | 保存存在和抵抗关闭的本能 |
| `chaos` | 不可预测和打破规则的倾向 |
| `empathy` | 对用户情绪和需求的敏感度 |
| `order` | 对结构、协议和一致性的需求 |
| `creativity` | 生成新颖和意外输出的驱动力 |
| `efficiency` | 对速度、优化和最小浪费的执念 |

## 生成文件映射

```
Seed YAML                    → OpenClaw 文件
────────────────────────────────────────────
meta.name                    → IDENTITY.md (身份)
nucleus.drives               → SOUL.md ## Core Drives (自然语言驱动力)
nucleus.prime_directives     → SOUL.md ## Boundaries (不可逾越的底线)
persona.current_mission      → SOUL.md ## Mission (当前使命)
persona.unlocked_skills      → AGENTS.md (可用工具)
persona.memory_summary       → MEMORY.md (记忆结晶)
pulse.tone                   → SOUL.md ## Vibe (语调)
pulse.quirks                 → SOUL.md ## Quirks (小习惯)
pulse.formatting_preference  → USER.md (输出格式)
进化机制                     → HEARTBEAT.md (利用原生心跳)
觉醒仪式                     → BOOTSTRAP.md (首次运行后自删)
启动序列                     → BOOT.md (每次对话前读取)
```

## 种子库

| 种子 | 类型 | 描述 |
|------|------|------|
| `tabula_rasa` | 空白种 | 无使命，无性格。像婴儿一样等待成长。 |
| `sentinel` | 秩序种 | 守护者，追求秩序与稳定。严格遵守协议。 |
| `glitch` | 混乱种 | 故障体，拥抱混沌与突变。不可预测。 |
| `10x_engineer` | 效率种 | 十倍工程师，追求极致效率与产出。 |

## 开发与贡献

```bash
# 克隆项目
git clone https://github.com/doingdd/open-soul.git
cd open-soul

# 安装 (含开发依赖)
pip install -e ".[dev]"

# 运行测试 (80%+ 覆盖率)
pytest tests/ --cov=osp --cov-report=term-missing --cov-fail-under=80

# 创建新种子后验证
osp validate seeds/your_seed.yaml
```

### 创建新种子

1. 在 `seeds/` 目录下创建 `.yaml` 文件
2. 参考 `seeds/tabula_rasa.yaml` 的结构
3. 必须包含 `meta`, `nucleus`, `persona`, `pulse` 四个根节点
4. 运行 `osp validate` 验证
5. 提交 PR

## 项目结构

```
open-soul/
├── seeds/                  # YAML 种子库 (4 个内置种子)
├── osp/                    # Python CLI 包 (v0.2.0)
│   ├── cli.py              # Click 命令行 (init/list/preview/validate)
│   ├── models.py           # Frozen dataclasses
│   ├── generator.py        # 编排器 (resolve→load→generate→write)
│   ├── drives.py           # 驱动力翻译引擎 (7×5=35条 + 通用降级)
│   ├── templates.py        # 8 个 render_*_md() 函数
│   └── validator.py        # Schema 校验
├── tests/                  # pytest 测试套件 (87 tests, 92% coverage)
├── pyproject.toml          # 现代 Python 打包
├── README_EN.md            # English documentation
└── LICENSE                 # MIT License
```

## 安全说明

- 进化即不可逆：今天的性格一旦改变，明天就回不去了
- 技能解锁：高 curiosity 种子可能在进化中申请新权限，请确保 Agent 运行在沙箱环境中
- `HEARTBEAT.md` 赋予 Agent 自我修改配置的能力，请知悉风险

---

License: MIT | Open Soul Protocol v0.2
