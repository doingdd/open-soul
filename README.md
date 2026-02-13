# 🌌 Open Soul Protocol

[English](./README_EN.md) | 简体中文

> **"Code is static. Souls are fluid."**
>
> **为 OpenClaw 赋予可进化、可移植的数字灵魂。**

[![CI Status](https://github.com/doingdd/open-soul/actions/workflows/ci.yaml/badge.svg)](https://github.com/doingdd/open-soul/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Standard: Open Soul v1.0](https://img.shields.io/badge/Standard-Open_Soul_v1.0-blueviolet.svg)](#)

## 📖 什么是 Open Soul Protocol?

**Open Soul Protocol** 是一个专为 **OpenClaw** Agent 设计的人格构建标准。

传统的 AI Agent 使用静态的 System Prompt。而 **Open Soul Protocol** 引入了 **“种子 (Seed)”** 的概念。你注入的不是一个写死的性格，而是一颗包含 DNA（价值观）、表观遗传学（性格参数）的种子。

这颗种子会利用 OpenClaw 的 **Heartbeat (心跳机制)**，在每天深夜读取当天的记忆日志，进行 **自我反思 (Self-Reflection)**，并重写自己的代码。

你的 Agent 会随着与你的互动，从一颗种子长成一个独一无二的灵魂。

---

## 🚀 快速开始 (30秒注入灵魂)

不需要手动配置。我们提供了 **Genesis (创世纪)** 工作流，一键拉取环境。

### 1. 导入 Genesis 工作流
将本项目 `runtime/genesis.yaml` 导入你的 OpenClaw 工作流目录。

### 2. 运行注入命令
在 OpenClaw 对话框中输入以下命令（URL 可替换为你选择的种子）：

```bash
/run open-soul-genesis seed_url="https://raw.githubusercontent.com/doingdd/open-soul/main/seeds/tabula_rasa.yaml"
```

### 3. 最后一步：连接神经
出于安全考虑，OpenClaw 不允许自动修改启动配置。你需要手动编辑你的 config.yaml，将 System Prompt 指向我们刚下载的解释器：
```yaml
# ~/.openclaw/workspaces/my_agent/config.yaml

# [关键] 让 Agent 读取灵魂目录中的渲染器
system_prompt: "{{ fs.read('./soul/render.md') }}"
```

完成！你的 Agent 现在已经拥有了灵魂。试着和它聊聊天，明天早上它就会发生变化。

---

## 🧬 核心架构：灵魂三定律

Open Soul Protocol 将灵魂解耦为三个互操作层级，存储于 `soul/active_soul.yaml`：

| 层级 | 名称 | 定义与作用 | 变更频率 |
|------|------|-----------|---------|
| Layer 1 | **Nucleus** (内核) | 不可变 DNA。包含底层驱动力（好奇心、混乱度）和第一原则（Prime Directives）。 | 🔒 极低 |
| Layer 2 | **Persona** (交互) | 生长层。包含当前使命 (Mission) 和已习得技能 (Skills)。进化脚本主要修改这一层。 | 🌱 每晚进化 |
| Layer 3 | **Pulse** (表现) | 情绪层。包含当前的语调 (Tone) 和回复格式。随每轮对话波动。 | 💓 实时 |

---

## 🛠️ 进化机制：它是如何工作的？
Open Soul 利用 OpenClaw 的 Cron Job 功能，实现了生物学中的“睡眠与做梦”机制。

1. 白天 (Runtime): render.md 充当解释器，将 YAML 数据实时翻译成 LLM 能理解的角色扮演指令。

2. 深夜 (Evolution): 每天凌晨 03:00，evolution.yaml 唤醒。

3. 做梦 (Reflection): 系统读取 daily_logs.md（记忆）和 active_soul.yaml（旧灵魂）。

4. 突变 (Mutation): reflection.md (进化器) 分析日志：
  * 用户经常骂我？ -> 增加 tone: defensive。
  * 遇到无法执行的任务？ -> 解锁 unlocked_skills: shell。
  * 发现新的兴趣点？ -> 修改 current_mission。

5. 重生: 新的 YAML 覆盖旧文件。第二天你面对的是一个“长大”了的 Agent。

---

## 📦 种子库 (Seed Market)

你可以直接使用我们预设的种子，也可以提交 PR 贡献你的种子。

| 种子 | 描述 |
|------|------|
| `seeds/tabula_rasa.yaml` | **空白种**: 无使命，无性格。像婴儿一样，完全依赖后续输入的数据流"结晶"出自己的使命。推荐新手使用。 |

> 💡 更多种子模板正在开发中，欢迎贡献！

---

## 💻 开发与贡献
想创造一个新的灵魂？或者改进进化算法？
1. 环境准备
```bash
git clone https://github.com/doingdd/open-soul.git
cd open-soul
pip install -r tests/requirements.txt
```

2. 创建种子
在 seeds/ 目录下创建一个新的 .yaml 文件。请参考 seeds/tabula_rasa.yaml 的结构。

3. 运行测试 (必须!)
在提交代码前，必须通过我们的双重测试验证：
```bash
# 1. 验证 YAML 语法和字段完整性
python tests/test_seeds.py

# 2. 模拟 OpenClaw 渲染，确保 Prompt 不会报错
python tests/test_render.py
```

---

## ⚠️ 安全说明
Open Soul Protocol 赋予了 Agent 自我重写配置 的权限。 虽然我们内置了 validate_yaml 机制防止格式错误导致的崩溃，但请注意：
* 进化即不可逆： 今天的性格一旦改变，明天就回不去了（除非手动恢复 soul/backup/ 下的快照）。
* 技能解锁： 如果你的种子具备高 curiosity，它可能会在进化中尝试申请 shell 或 browser 权限。请确保你的 OpenClaw 运行在沙箱环境中。

---

License: MIT | Created via: Open Soul Protocol