# Open Soul Protocol - Claude Code Context

> **为 AI 助手提供的项目上下文文档**

## 项目概述

**Open Soul Protocol (SSOP)** 是一个为 OpenClaw Agent 设计的人格构建标准。它通过"种子"概念让 AI Agent 具备可进化、可移植的数字灵魂。

### 核心理念

- **Seed (种子)**: 包含 DNA（价值观）和性格参数的 YAML 配置文件
- **Evolution (进化)**: 每日深夜的自我反思和重写机制
- **Three Layers**: Nucleus（内核）→ Persona（交互）→ Pulse（表现）

---

## 项目结构

```
open-soul/
├── seeds/                  # 灵魂种子库
│   └── tabula_rasa.yaml    # 空白种（默认）
├── runtime/                # 运行时组件
│   ├── render.md           # Jinja2 模板：将 YAML 渲染为 System Prompt
│   ├── reflection.md       # 进化引擎：LLM Prompt 模板
│   ├── genesis.yaml        # 初始化工作流
│   └── evolution.yaml      # 每日进化工作流
├── spec/                   # 规范文档
│   ├── schema.json         # JSON Schema 定义
│   └── ssop_v1.md          # 协议规范文档
├── tests/                  # 测试套件
│   ├── test_seeds.py       # 验证 YAML 语法和 Schema
│   ├── test_render.py      # 模拟 OpenClaw 渲染
│   └── requirements.txt    # Python 依赖
├── tools/                  # 工具脚本
│   ├── validate_seeds.py
│   └── test_render.py
└── .github/workflows/
    └── ci.yaml             # GitHub Actions CI
```

---

## 开发命令

<!-- AUTO-GENERATED: Scripts Reference -->
| 命令 | 描述 |
|------|------|
| `python3 tests/test_seeds.py` | 验证所有 seed 的 YAML 语法和 Schema 完整性 |
| `python3 tests/test_render.py` | 模拟 OpenClaw 渲染，确保 Prompt 生成正常 |
| `pip install -r tests/requirements.txt` | 安装测试依赖 (pyyaml, jinja2, jsonschema) |

### 完整测试流程

```bash
# 安装依赖
pip install -r tests/requirements.txt

# 运行所有测试（提交前必须通过）
python3 tests/test_seeds.py && python3 tests/test_render.py
```

---

## 灵魂三层架构

### Layer 1: Nucleus (内核) 🔒
- **变更频率**: 极低（几乎不可变）
- **内容**: 底层驱动力 (drives) 和第一原则 (prime_directives)
- **示例字段**:
  - `drives.curiosity`: 0.0-1.0，好奇心强度
  - `drives.chaos`: 0.0-1.0，混乱度
  - `prime_directives`: 不可逾越的底线指令列表

### Layer 2: Persona (交互) 🌱
- **变更频率**: 每晚进化
- **内容**: 当前使命、记忆结晶、已解锁技能
- **示例字段**:
  - `current_mission`: 动态目标
  - `mission_lock`: 是否锁定使命
  - `memory_summary`: 过往经历总结
  - `unlocked_skills`: 可用工具列表

### Layer 3: Pulse (表现) 💓
- **变更频率**: 实时波动
- **内容**: 语调、回复格式、口头禅
- **示例字段**:
  - `tone`: 语气关键词列表
  - `formatting_preference`: 输出格式偏好
  - `quirks`: 强制性小习惯

---

## 创建新 Seed

1. 在 `seeds/` 目录下创建新的 `.yaml` 文件
2. 参考 `seeds/tabula_rasa.yaml` 的结构
3. 必须包含以下根节点: `meta`, `nucleus`, `persona`, `pulse`
4. 运行测试验证:

```bash
python3 tests/test_seeds.py
python3 tests/test_render.py
```

---

## 测试验证标准

### test_seeds.py 验证项
- [ ] YAML 语法正确
- [ ] 包含所有必需的根节点 (meta, nucleus, persona, pulse)
- [ ] nucleus 包含 drives 和 prime_directives
- [ ] persona 包含 current_mission, unlocked_skills, memory_summary
- [ ] pulse 包含 tone 和 formatting_preference
- [ ] drives 数值在 0.0-1.0 范围内

### test_render.py 验证项
- [ ] render.md 模板可以成功渲染
- [ ] 输出包含 "LAYER 1: NUCLEUS" 标题
- [ ] Persona 的 mission 被正确渲染

---

## 进化机制

```
白天 (Runtime)
    ↓
render.md 实时翻译 YAML → System Prompt
    ↓
深夜 03:00 (Evolution)
    ↓
evolution.yaml 触发
    ↓
reflection.md 分析 daily_logs.md
    ↓
生成新的 active_soul.yaml
    ↓
第二天：面对"长大"的 Agent
```

---

## 注意事项

1. **本地测试优先**: 提交前必须在本地运行测试并全部通过
2. **路径规范**: 测试文件使用基于仓库根目录的相对路径 (如 `seeds/` 而非 `../seeds/`)
3. **Jinja2 兼容**: `render.md` 中的模板语法需要兼容 Jinja2，避免使用 `>` 符号在 `{% %}` 附近
4. **YAML 安全**: evolution.yaml 包含 YAML 格式验证，防止脏数据覆盖

---

## 相关链接

- **GitHub**: https://github.com/doingdd/open-soul
- **CI Status**: https://github.com/doingdd/open-soul/actions
