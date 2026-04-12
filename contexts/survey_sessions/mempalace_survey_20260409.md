# MemPalace 深度调研报告

**调研日期**: 2026-04-09  
**调研对象**: MemPalace - AI Agent 长期记忆系统  
**版本**: v3.0.0  
**来源**: [GitHub](https://github.com/milla-jovovich/mempalace) | [官网](https://mempalace.info) | [Product Hunt](https://www.producthunt.com/products/mempalace)

---

## 核心概述

MemPalace 是一个开源的 AI Agent 长期记忆系统，由 Milla Jovovich 开发，采用 2,500 年历史的记忆宫殿（Method of Loci）技术，实现 **96.6% 的召回率**（LongMemEval 基准测试），仅需 **170 tokens 启动成本**，完全本地运行，零 API 费用。

> **关键指标**（[GitHub README](https://github.com/milla-jovovich/mempalace/blob/main/README.md)）：
> - GitHub Stars: 27K+
> - LongMemEval R@5: 96.6%（原始模式）
> - 启动成本: 170 tokens
> - 年度成本: ~$10（对比 LLM 摘要方式 $507/年）
> - 许可证: MIT

---

## 1. MCP 集成 - 19 个工具详解

MemPalace 通过 MCP (Model Context Protocol) 协议提供 **19 个工具**，分为 6 个类别：

### 1.1 Palace 读取工具（7 个）

| 工具名 | 功能描述 |
|--------|----------|
| `mempalace_status` | 获取宫殿概览 + AAAK 规范 + 记忆协议 |
| `mempalace_list_wings` | 列出所有 Wings 及其抽屉数量 |
| `mempalace_list_rooms` | 列出特定 Wing 内的所有 Rooms |
| `mempalace_get_taxonomy` | 获取完整的 Wing → Room → Count 树 |
| `mempalace_search` | 语义搜索，支持 Wing/Room 过滤 |
| `mempalace_check_duplicate` | 归档前检查内容是否已存在 |
| `mempalace_get_aaak_spec` | 获取 AAAK 方言参考 |

### 1.2 Palace 写入工具（2 个）

| 工具名 | 功能描述 |
|--------|----------|
| `mempalace_add_drawer` | 将原文内容归档到 Wing/Room |
| `mempalace_delete_drawer` | 通过 ID 删除抽屉 |

### 1.3 知识图谱工具（5 个）

| 工具名 | 功能描述 |
|--------|----------|
| `mempalace_kg_query` | 实体关系查询，支持时间过滤 |
| `mempalace_kg_add` | 添加事实 |
| `mempalace_kg_invalidate` | 标记事实已结束 |
| `mempalace_kg_timeline` | 实体时间线故事 |
| `mempalace_kg_stats` | 图谱概览 |

### 1.4 导航工具（3 个）

| 工具名 | 功能描述 |
|--------|----------|
| `mempalace_traverse` | 从 Room 跨 Wings 遍历图谱 |
| `mempalace_find_tunnels` | 查找连接两个 Wings 的 Rooms |
| `mempalace_graph_stats` | 图谱连通性概览 |

### 1.5 Agent Diary 工具（2 个）

| 工具名 | 功能描述 |
|--------|----------|
| `mempalace_diary_write` | 写入 AAAK 日记条目 |
| `mempalace_diary_read` | 读取最近日记条目 |

**来源**: [GitHub - MCP Server 章节](https://github.com/milla-jovovich/mempalace/blob/main/README.md#mcp-server)

---

## 2. Claude Code 插件集成

### 2.1 安装方式

**通过 Claude Code Marketplace（推荐）**：

```bash
# 添加 marketplace
claude plugin marketplace add milla-jovovich/mempalace

# 安装插件
claude plugin install --scope user mempalace
```

**本地安装**：

```bash
claude plugin add /path/to/mempalace
```

### 2.2 安装后设置

运行初始化命令完成设置：

```bash
/mempalace:init
```

这会执行：
- pip 安装 mempalace
- MCP 配置
- 初始化向导（创建 palace、生成 AAAK 引导）

### 2.3 可用的 Slash 命令

| 命令 | 描述 |
|------|------|
| `/mempalace:help` | 显示可用工具、技能和架构 |
| `/mempalace:init` | 设置 MemPalace |
| `/mempalace:search` | 搜索记忆 |
| `/mempalace:mine` | 挖掘项目和对话 |
| `/mempalace:status` | 显示宫殿状态 |

### 2.4 自动保存 Hooks

插件自动注册两个 hooks：

- **Save Hook**: 每 15 条消息触发，结构化保存话题、决策、引用、代码变更
- **PreCompact Hook**: 上下文压缩前触发，紧急保存

**配置**（在 `.claude/settings.local.json`）：

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "/absolute/path/to/hooks/mempal_save_hook.sh",
        "timeout": 30
      }]
    }],
    "PreCompact": [{
      "hooks": [{
        "type": "command",
        "command": "/absolute/path/to/hooks/mempal_precompact_hook.sh",
        "timeout": 30
      }]
    }]
  }
}
```

**来源**: [GitHub - .claude-plugin/README.md](https://github.com/milla-jovovich/mempalace/blob/main/.claude-plugin/README.md)

---

## 3. 其他 AI 工具集成

### 3.1 ChatGPT / Cursor（MCP 兼容）

```bash
# 连接 MemPalace（只需一次）
claude mcp add mempalace -- python -m mempalace.mcp_server

# 现在你的 AI 可以自动调用 19 个工具
# 例如："What did we decide about auth last month?"
# Claude 会自动调用 mempalace_search
```

### 3.2 Codex CLI (OpenAI)

**安装方式**：

```bash
# 复制或 symlink 插件目录到项目根目录
cp -r .codex-plugin /path/to/your/project/.codex-plugin

# 验证插件
codex --plugins

# 初始化宫殿
codex /init
```

**或通过 Git 安装**：

```bash
git clone https://github.com/milla-jovovich/mempalace.git
cd mempalace
pip install -e .
# .codex-plugin 目录已在 repo 根目录，Codex CLI 会自动检测
```

**可用技能**：
- `/help` - 显示命令
- `/init` - 初始化宫殿
- `/search` - 语义搜索
- `/mine` - 挖掘项目
- `/status` - 显示状态

**Hooks 配置**（在 `.codex/hooks.json`）：

```json
{
  "Stop": [{
    "type": "command",
    "command": "/absolute/path/to/hooks/mempal_save_hook.sh",
    "timeout": 30
  }],
  "PreCompact": [{
    "type": "command",
    "command": "/absolute/path/to/hooks/mempal_precompact_hook.sh",
    "timeout": 30
  }]
}
```

**来源**: [GitHub - .codex-plugin/README.md](https://github.com/milla-jovovich/mempalace/blob/main/.codex-plugin/README.md)

### 3.3 Gemini CLI

**安装步骤**：

```bash
# 1. 克隆仓库
git clone https://github.com/milla-jovovich/mempalace.git
cd mempalace

# 2. 创建虚拟环境
python3 -m venv .venv

# 3. 安装依赖
.venv/bin/pip install -e .

# 4. 初始化宫殿
.venv/bin/python3 -m mempalace init .
```

**连接 MCP**：

```bash
gemini mcp add mempalace /absolute/path/to/mempalace/.venv/bin/python3 -m mempalace.mcp_server --scope user
```

**启用自动保存**（编辑 `~/.gemini/settings.json`）：

```json
{
  "hooks": {
    "PreCompress": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "/absolute/path/to/mempalace/hooks/mempal_precompact_hook.sh"
          }
        ]
      }
    ]
  }
}
```

**验证**：
- `/mcp list` - 验证 `mempalace` 为 `CONNECTED`
- `/hooks panel` - 验证 `PreCompress` hook 已激活

**来源**: [GitHub - examples/gemini_cli_setup.md](https://github.com/milla-jovovich/mempalace/blob/main/examples/gemini_cli_setup.md)

---

## 4. 本地模型支持（Llama、Mistral 等）

本地模型通常不支持 MCP，提供两种方式：

### 4.1 Wake-up 命令

将世界信息加载到模型上下文中：

```bash
# 生成上下文
mempalace wake-up > context.txt

# 将 context.txt 粘贴到本地模型的 system prompt
# 提供约 170 tokens 的关键信息
```

### 4.2 CLI 搜索

按需查询，将结果注入 prompt：

```bash
mempalace search "auth decisions" > results.txt
# 在 prompt 中包含 results.txt
```

### 4.3 Python API

```python
from mempalace.searcher import search_memories

results = search_memories("auth decisions", palace_path="~/.mempalace/palace")
# 将结果注入本地模型上下文
```

**优势**：
- 完整离线：ChromaDB 本地 + Llama/Mistral 本地
- 可使用 AAAK 压缩
- 零云端调用

**来源**: [GitHub README - With local models 章节](https://github.com/milla-jovovich/mempalace/blob/main/README.md#with-local-models-llama-mistral-or-any-offline-llm)

---

## 5. 实际使用场景

### 5.1 个人开发者跨项目管理

**场景**：同时维护多个项目（Orion、Nova、Helios），需要记住每个项目的历史决策。

**Workflow**：

```bash
# 为每个项目挖掘对话记录
mempalace mine ~/chats/orion/  --mode convos --wing orion
mempalace mine ~/chats/nova/   --mode convos --wing nova
mempalace mine ~/chats/helios/ --mode convos --wing helios

# 六个月后询问："为什么这个项目用 Postgres？"
mempalace search "database decision" --wing orion
# → "Chose Postgres over SQLite because Orion needs concurrent writes 
#    and the dataset will exceed 10GB. Decided 2025-11-03."

# 跨项目搜索
mempalace search "rate limiting approach"
# → 找到 Orion 和 Nova 的不同实现方式
```

**来源**: [GitHub README - Solo developer 章节](https://github.com/milla-jovovich/mempalace/blob/main/README.md#solo-developer-across-multiple-projects)

### 5.2 团队领导管理产品

**场景**：管理 Driftwood 产品团队，需要追踪谁做了什么决策。

**Workflow**：

```bash
# 挖掘 Slack 导出和 AI 对话
mempalace mine ~/exports/slack/ --mode convos --wing driftwood
mempalace mine ~/.claude/projects/ --mode convos

# "Soren 上个冲刺做了什么？"
mempalace search "Soren sprint" --wing driftwood
# → 14 个 closets：OAuth 重构、暗黑模式、组件库迁移

# "谁决定使用 Clerk？"
mempalace search "Clerk decision" --wing driftwood
# → "Kai 推荐 Clerk 替代 Auth0 — 价格 + 开发体验。
#    团队 2026-01-15 同意。Maya 负责迁移。"
```

**来源**: [GitHub README - Team lead 章节](https://github.com/milla-jovovich/mempalace/blob/main/README.md#team-lead-managing-a-product)

### 5.3 自动保存 Hooks 的使用

**配置 Save Hook**（每 15 条消息保存）：

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "/path/to/mempalace/hooks/mempal_save_hook.sh",
        "timeout": 30
      }]
    }]
  }
}
```

**工作流程**：
1. 用户发送消息 → AI 响应 → 触发 Stop hook
2. Hook 计数人类消息（检查是否 ≥15 条）
3. 达到阈值：Hook 返回 `{"decision": "block", "reason": "save..."}`
4. AI 看到 block，将关键话题/决策/引用保存到宫殿
5. AI 再次尝试停止 → 这次通过

**PreCompact Hook**（紧急保存）：
- 在上下文压缩前 ALWAYS 触发
- 强制 AI 保存所有内容
- 防止窗口压缩导致记忆丢失

**环境变量**（可选自动挖掘）：

```bash
export MEMPAL_DIR="/path/to/conversations"
# 每次 save trigger 时自动运行 mempalace mine $MEMPAL_DIR
```

**来源**: [GitHub - hooks/README.md](https://github.com/milla-jovovich/mempalace/blob/main/hooks/README.md)

---

## 6. 三种 Mining 模式详解

### 6.1 Projects 模式

**用途**：挖掘项目文件（代码、文档、笔记）

```bash
mempalace mine ~/projects/myapp
```

**处理内容**：
- 源代码文件
- Markdown 文档
- 配置文件
- README、CHANGELOG 等

### 6.2 Convos 模式

**用途**：挖掘对话导出（Claude、ChatGPT、Slack）

```bash
mempalace mine ~/chats/ --mode convos
mempalace mine ~/chats/ --mode convos --wing myapp  # 指定 wing
```

**支持格式**：
- JSONL（Claude Code 导出）
- JSON（ChatGPT 导出）
- Markdown 对话记录

**预处理**（分割大文件）：

```bash
# 如果导出文件包含多个会话
mempalace split ~/chats/                      # 分割
mempalace split ~/chats/ --dry-run            # 预览
mempalace split ~/chats/ --min-sessions 3     # 仅分割含 3+ 会话的文件
```

### 6.3 General 模式

**用途**：自动分类为决策、里程碑、问题、偏好、情感

```bash
mempalace mine ~/chats/ --mode convos --extract general
```

**自动分类**：
- **Decisions** - 做出的选择
- **Milestones** - 重要节点
- **Problems** - 遇到的问题
- **Preferences** - 偏好设置
- **Emotional context** - 情感背景

**来源**: [GitHub README - Quick Start](https://github.com/milla-jovovich/mempalace/blob/main/README.md#quick-start)

---

## 7. Agent Diary 功能 - 专家 Agent 记忆管理

### 7.1 架构设计

每个专家 Agent 在宫殿中拥有自己的 Wing 和 Diary：

```
~/.mempalace/agents/
  ├── reviewer.json       # 代码质量、模式、Bug
  ├── architect.json      # 设计决策、权衡
  └── ops.json            # 部署、事件、基础设施
```

**CLAUDE.md 仅需一行**：

```
You have MemPalace agents. Run mempalace_list_agents to see them.
```

### 7.2 Agent 工作流

**每个 Agent 具备**：
- **Focus** - 关注领域
- **Diary** - 用 AAAK 编写，跨会话持久化
- **Expertise** - 阅读自身历史保持领域敏锐

**写入日记**：

```bash
mempalace_diary_write("reviewer",
    "PR#42|auth.bypass.found|missing.middleware.check|pattern:3rd.time.this.quarter|★★★★")
```

**读取历史**：

```bash
mempalace_diary_read("reviewer", last_n=10)
# → 最近 10 条发现，AAAK 压缩格式
```

### 7.3 对比方案

| 特性 | MemPalace | Letta |
|------|-----------|-------|
| 成本 | 免费 | $20-200/月 |
| Agent 记忆 | 一个 Wing | 托管服务 |
| 控制 | 完全本地 | 云端 |

**来源**: [GitHub README - Specialist Agents 章节](https://github.com/milla-jovovich/mempalace/blob/main/README.md#specialist-agents)

---

## 8. 使用限制与前提条件

### 8.1 系统要求

- **Python**: 3.9+
- **依赖**: `chromadb>=0.4.0`, `pyyaml>=6.0`
- **存储**: SQLite（本地）+ ChromaDB（向量数据库）

### 8.2 安装

```bash
# PyPI 安装
pip install mempalace

# 或使用 uv（推荐）
uv pip install mempalace

# 从源码
pip install -e .
```

### 8.3 初始化

```bash
mempalace init ~/projects/myapp
```

这会创建：
- Palace 目录结构（Wings、Rooms、Closets、Drawers）
- 配置文件（`~/.mempalace/config.json`）
- 身份文件（`~/.mempalace/identity.txt`）
- Wing 配置（`~/.mempalace/wing_config.json`）

### 8.4 已知限制

1. **AAAK 压缩**（实验性）：
   - 当前在 LongMemEval 上得分 **84.2%**（对比原始模式 96.6%）
   - 小文本不节省 tokens（开销超过收益）
   - 仅在重复实体多时有效

2. **矛盾检测**（实验性）：
   - 工具 `fact_checker.py` 存在但未自动集成到知识图谱操作
   - 需手动调用（Issue #27 追踪）

3. **平台兼容性**：
   - Issue #100: 需固定 ChromaDB 版本范围
   - Issue #74: macOS ARM64 段错误（处理中）
   - Issue #110: hooks 中的 shell 注入风险（处理中）

**来源**: [GitHub README - A Note from Milla & Ben](https://github.com/milla-jovovich/mempalace/blob/main/README.md#a-note-from-milla--ben--april-7-2026)

---

## 9. 性能基准测试

### 9.1 LongMemEval（行业标准）

| 模式 | R@5 | API 调用 | 可复现性 |
|------|-----|----------|----------|
| **MemPalace (hybrid)** | **100%** | 可选 | 是 |
| MemPalace (raw) | **96.6%** | 零 | 是 |
| Supermemory ASMR | ~99% | 是 | — |
| Mastra | 94.87% | 是 (GPT) | — |
| Mem0 | ~85% | 是 | — |
| Zep | ~85% | 是 | — |

### 9.2 其他基准

| 基准测试 | 模式 | 得分 | API 调用 |
|----------|------|------|----------|
| LoCoMo R@10 | Raw, session level | 60.3% | 零 |
| Personal palace R@10 | Heuristic | 85% | 零 |
| Palace structure | Wing+room 过滤 | +34% R@10 | 零 |

**复现方法**：见 `benchmarks/` 目录

```bash
cd benchmarks
python longmemeval_bench.py
```

**来源**: [GitHub - Benchmarks 章节](https://github.com/milla-jovovich/mempalace/blob/main/README.md#benchmarks)

---

## 10. 竞品对比

| 框架 | 召回率 | 启动成本 | 定价 | 本地运行 | 许可证 |
|------|--------|----------|------|----------|--------|
| **MemPalace** | **96.6%** | **170 tokens** | **免费** | **是** | **MIT** |
| Mem0 | ~85% | ~2K tokens | $19-249/月 | 部分 | Apache 2.0 |
| Zep | ~80% | ~5K tokens | $25/月+ | 否 | 专有 |
| LangChain Memory | ~70% | 可变 | API 费用 | 部分 | MIT |

**关键差异**：
- MemPalace 存储原始文本（非摘要）
- 零 API 依赖
- 空间层级结构（Wings → Rooms → Closets → Drawers）

**来源**: [mempalace.info/compare](https://mempalace.info/compare)

---

## 11. 核心概念：宫殿架构

### 11.1 空间层级

```
WING (项目/人物)
  ├── HALL (记忆类型)
  │     ├── ROOM (主题)
  │     │     ├── CLOSET (摘要)
  │     │     │     └── DRAWER (原始文件)
```

- **Wings**: 顶级分类（人员、项目）
- **Halls**: 记忆类型走廊
  - `hall_facts` - 决策
  - `hall_events` - 会话、里程碑
  - `hall_discoveries` - 突破
  - `hall_preferences` - 偏好
  - `hall_advice` - 建议
- **Rooms**: 特定主题（`auth-migration`、`graphql-switch`）
- **Tunnels**: 跨 Wings 连接相同 Room
- **Closets**: 指向原始内容的摘要
- **Drawers**: 原始文件（永不摘要）

### 11.2 记忆堆栈（4 层）

| 层级 | 内容 | 大小 | 加载时机 |
|------|------|------|----------|
| L0 | 身份（AI 是谁） | ~50 tokens | 始终 |
| L1 | 关键事实（团队、项目、偏好） | ~120 tokens | 始终 |
| L2 | Room 召回（最近会话、当前项目） | 按需 | 话题出现时 |
| L3 | 深度搜索（语义查询所有 closets） | 按需 | 明确询问时 |

**启动时加载 L0 + L1**（~170 tokens），搜索仅在需要时触发。

**来源**: [GitHub README - The Memory Stack](https://github.com/milla-jovovich/mempalace/blob/main/README.md#the-memory-stack)

---

## 12. 总结与建议

### 12.1 适用场景

✅ **推荐使用**：
- 长期维护多个项目的独立开发者
- 需要追踪团队决策的技术负责人
- 希望 AI 记住历史上下文的用户
- 注重隐私（完全本地运行）
- 希望降低 API 成本

❌ **不建议使用**：
- 需要 100% 云端访问（多设备同步未原生支持）
- 不愿处理本地数据库维护
- 对实验性功能（AAAK）稳定性要求高

### 12.2 快速开始检查清单

- [ ] Python 3.9+ 已安装
- [ ] `pip install mempalace`
- [ ] `mempalace init <dir>` 初始化
- [ ] 挖掘现有对话/项目
- [ ] 安装 Claude Code 插件或配置 MCP
- [ ] （可选）配置自动保存 hooks

### 12.3 资源链接

- **GitHub**: https://github.com/milla-jovovich/mempalace
- **文档**: https://mempalace.info/guide
- **Product Hunt**: https://www.producthunt.com/products/mempalace
- **Discord**: https://discord.com/invite/ycTQQCu6kn

---

*报告生成时间: 2026-04-09*  
*调研方法: Web 抓取 + 官方文档分析*