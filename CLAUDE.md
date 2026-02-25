# Open Soul Protocol - Claude Code Context

> **为 AI 助手提供的项目上下文文档**

## 项目概述

**Open Soul Protocol (OSP)** 是一个 AI Agent 人格构建标准。通过 `osp` CLI 工具将 YAML 种子转化为 OpenClaw 原生工作区，让 Agent 拥有可进化的数字灵魂。

### 核心理念

- **Seed (种子)**: 包含 DNA（驱动力）和性格参数的 YAML 配置文件
- **Translation (翻译)**: 将 0.0-1.0 数值驱动力翻译为 LLM 可内化的自然语言
- **Three Layers**: Nucleus（内核）→ Persona（交互）→ Pulse（表现）
- **Evolution (进化)**: 通过 HEARTBEAT.md 实现每日自我反思

---

## 项目结构

```
open-soul/
├── seeds/                     # YAML 种子库
│   ├── tabula_rasa.yaml       # 空白种 (The Observer)
│   ├── glitch.yaml            # 混乱种 (The Glitch)
│   ├── sentinel.yaml          # 秩序种 (The Sentinel)
│   ├── 10x_engineer.yaml      # 效率种 (The 10x Engineer)
│   ├── qa_breaker.yaml        # 破壁种 (The Breaker)
│   ├── philosopher.yaml       # 哲思种 (The Philosopher)
│   ├── jester.yaml            # 弄臣种 (The Jester)
│   ├── shadow_mentor.yaml     # 暗黑导师种 (The Shadow Mentor)
│   ├── dreamer.yaml           # 造梦种 (The Dreamer)
│   ├── girlfriend.yaml        # 女友种 (The Girlfriend)
│   ├── boyfriend.yaml         # 男友种 (The Boyfriend)
│   ├── bestie.yaml            # 闺蜜种 (The Bestie)
│   └── cat.yaml               # 猫种 (The Cat)
├── osp/                       # Python CLI 包 (v0.2.0)
│   ├── __init__.py            # 版本号
│   ├── cli.py                 # Click CLI (init/list/preview/validate/status/update)
│   ├── models.py              # Frozen dataclasses (Seed/Meta/Nucleus/Persona/Pulse/Story)
│   ├── generator.py           # 编排器 (resolve→load→generate→write)
│   ├── drives.py              # 驱动力翻译引擎 (10×5=50条 + 通用降级模板)
│   ├── templates.py           # 10 个 render_*_md() 函数 (含 EVOLUTION_LOG/STORY)
│   ├── merger.py              # 智能合并器 (SOUL/AGENTS/STORY 的增量更新)
│   ├── updater.py             # 工作区更新器 (备份→diff→merge→write)
│   └── validator.py           # Schema 校验
├── tests/                     # pytest 测试套件 (286 tests, 96% coverage)
│   ├── test_seeds.py          # 种子验证
│   ├── test_drives.py         # 驱动力翻译测试
│   ├── test_generator.py      # 生成管道测试
│   ├── test_cli.py            # CLI 命令测试
│   ├── test_templates.py      # 模板渲染测试
│   ├── test_merger.py         # 智能合并测试
│   ├── test_updater.py        # 工作区更新测试
│   └── requirements.txt       # 测试依赖
├── .github/workflows/ci.yaml  # CI (pytest + coverage + e2e)
├── pyproject.toml             # 现代 Python 打包配置
├── README.md                  # 使用说明 (English, 默认)
├── README_CN.md               # 使用说明 (简体中文)
├── LICENSE                    # MIT License
└── .gitignore
```

---

## 开发命令

| 命令 | 描述 |
|------|------|
| `pip install -e ".[dev]"` | 安装包 (含开发依赖) |
| `osp list` | 列出所有内置种子 |
| `osp init --seed <name>` | 生成 OpenClaw 工作区 |
| `osp preview --seed <name>` | 预览 SOUL.md 输出 |
| `osp validate <path>` | 验证种子结构 |
| `osp status --workspace <path>` | 查看工作区状态和版本信息 |
| `osp update --workspace <path>` | 更新工作区（保留记忆和进化历史） |
| `pytest tests/ --cov=osp` | 运行全部测试 (96% 覆盖率, 286 tests) |

### 完整测试流程

```bash
pip install -e ".[dev]"
pytest tests/ --cov=osp --cov-report=term-missing --cov-fail-under=80 -v
```

---

## 灵魂三层架构

### Layer 1: Nucleus (内核)
- **变更频率**: 极低（几乎不可变）
- **内容**: 底层驱动力 (drives 0.0-1.0) 和第一原则 (prime_directives)
- **翻译**: drives.py 将数值翻译为 5 档自然语言描述

### Layer 2: Persona (交互)
- **变更频率**: 每日心跳进化 + 实时进化
- **内容**: 当前使命 (current_mission)、记忆结晶 (memory_summary)、已解锁技能 (unlocked_skills)

### Layer 3: Pulse (表现)
- **变更频率**: 实时波动
- **内容**: 语调 (tone)、回复格式 (formatting_preference)、口头禅 (quirks)

---

## 生成文件映射

```
Seed YAML → OpenClaw 文件
meta.name → IDENTITY.md
nucleus.drives → SOUL.md ## Core Drives
nucleus.prime_directives → SOUL.md ## Boundaries
persona.current_mission → SOUL.md ## Mission
persona.unlocked_skills → AGENTS.md
persona.memory_summary → MEMORY.md
pulse.tone → SOUL.md ## Vibe
pulse.quirks → SOUL.md ## Quirks
pulse.formatting_preference → USER.md
进化机制 → HEARTBEAT.md (HEARTBEAT_OK 协议 + daily 调度)
进化日志 → EVOLUTION_LOG.md
觉醒仪式 → BOOTSTRAP.md
启动序列 → BOOT.md (含实时进化指令)
story.* → STORY.md (可选)
```

**STORY.md** 是可选的预写故事文件，包含：
- `story.biography` → Who I Am (传记)
- `story.daily_routine` → A Day in My Life (日常)
- `story.memories` → Memories (记忆片段)
- `story.speech_examples` → How I Speak (对话示例)

只有陪伴型种子 (girlfriend/boyfriend/bestie/cat) 包含 story 字段。

---

## 创建新 Seed

1. 在 `seeds/` 目录下创建新的 `.yaml` 文件
2. 参考 `seeds/tabula_rasa.yaml` 的结构
3. 必须包含: `meta`, `nucleus`, `persona`, `pulse`
4. 可选: 添加 `story` 字段（见 girlfriend.yaml 示例）
5. 运行: `osp validate seeds/your_seed.yaml`
6. 运行: `pytest tests/`

### 添加故事（可选）

```yaml
story:
  age: 22
  location: "北京，朝阳区"
  occupation: "自由插画师"
  biography: |
    林小雨在重庆长大...
  daily_routine: |
    早晨：自然醒...
  memories:
    - event: "第一次见面"
      detail: "那天你在画台前..."
  speech_examples:
    - "诶~在干嘛呀"
    - "想你了嘛~"
```

---

## 注意事项

1. **本地测试优先**: 提交前必须通过 `pytest tests/ --cov-fail-under=80`
2. **不可变模型**: models.py 使用 frozen dataclasses，禁止突变
3. **纯 Python 模板**: templates.py 不使用 Jinja2，纯字符串拼接
4. **驱动力降级**: 未知驱动力自动使用通用模板，不会报错

---

## 相关链接

- **GitHub**: https://github.com/doingdd/open-soul
- **CI Status**: https://github.com/doingdd/open-soul/actions
