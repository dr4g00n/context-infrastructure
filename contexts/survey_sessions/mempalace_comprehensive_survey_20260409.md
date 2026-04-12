# MemPalace 开源 AI 记忆系统深度调研报告

**调研日期**: 2026-04-09  
**项目地址**: https://github.com/milla-jovovich/mempalace  
**调研方法**: 多维度并行调研 + 交叉验证

---

## 核心结论

**MemPalace** 是一个开源 AI 长期记忆系统，采用"记忆宫殿"隐喻架构，主打**纯本地、零 API 依赖、高召回率**。

### 关键数据速览

| 指标 | 数据 | 说明 |
|------|------|------|
| GitHub Stars | **26.9k** | 快速增长中（2026-04-09） |
| LongMemEval R@5 | **96.6%** | Raw 模式，零 API 调用（最高零依赖得分） |
| 启动成本 | **~170 tokens** | L0 + L1 记忆栈 |
| 年成本 | **$0.70** | 对比 LLM 摘要方案 $507/年 |
| 许可证 | **MIT** | 完全开源免费 |

### 核心争议

项目在发布 48 小时内因夸大宣传（"30x lossless compression"、"+34% palace boost"）引发社区质疑，作者于 **2026-04-07 发布更正声明**，承认问题并承诺修复。

---

## 一、项目概述

### 1.1 什么是 MemPalace

MemPalace 是一个**本地优先**的 AI 记忆系统，设计理念源自古希腊演说家的"记忆宫殿"技巧：

> 通过将信息放置在想象中的建筑物房间里，人类可以在需要时通过"漫步"建筑来检索记忆。MemPalace 将这一原则应用于 AI 记忆——对话被组织成 wings（人员/项目）、halls（记忆类型）和 rooms（具体主题）。

**官方定位**（[GitHub README](https://github.com/milla-jovovich/mempalace)）：
- "史上基准测试得分最高的 AI 记忆系统，而且是免费的"
- "存储一切，然后让信息可检索"
- 与其他系统的区别：不依赖 AI 判断"什么值得记住"

### 1.2 核心差异化

| 特性 | MemPalace | 其他记忆系统 |
|------|-----------|-------------|
| 存储策略 | 原始 verbatim 全文 | LLM 摘要/提取 |
| 架构 | 结构化 Palace（wings/rooms/halls） | 扁平向量索引 |
| 部署 | 纯本地，零云端 | 托管/混合 |
| 成本 | 完全免费 | $19-249/月 |

---

## 二、技术架构深度解析

### 2.1 Palace 结构：五层隐喻

MemPalace 使用建筑隐喻组织记忆：

```
┌─────────────────────────────────────────────────────────────┐
│  WING (翼) —— 人员或项目                                      │
│  例如：wing_kai, wing_driftwood                               │
│                                                              │
│    ┌──────────┐  ── HALL (厅) ──  ┌──────────┐              │
│    │  Room A  │                   │  Room B  │              │
│    │(auth迁移)│                   │(性能优化)│              │
│    └────┬─────┘                   └──────────┘              │
│         │                                                    │
│         ▼                                                    │
│    ┌──────────┐      ┌──────────┐                          │
│    │  Closet  │ ───▶ │  Drawer  │                          │
│    │ (摘要索引)│      │(原始全文)│                          │
│    └──────────┘      └──────────┘                          │
└─────────────────────────────────────────────────────────────┘
           │
         TUNNEL (隧道) —— 跨 Wing 连接相同 Room
           │
┌──────────┼──────────────────────────────────────────────────┐
│  WING: Project                                             │
│         │                                                   │
│    ┌────┴─────┐                                            │
│    │  Room A  │ ←── 同名 Room 自动关联                     │
│    │(auth迁移)│                                            │
└─────────────────────────────────────────────────────────────┘
```

**组件详解**：

| 组件 | 作用 | 示例 |
|------|------|------|
| **Wing** | 顶级容器，按人员或项目划分 | `wing_kai`, `wing_driftwood` |
| **Hall** | 记忆类型走廊，横向分类 | `hall_facts`（决策）、`hall_events`（事件）、`hall_advice`（建议） |
| **Room** | 具体主题房间 | `auth-migration`, `graphql-switch` |
| **Tunnel** | 跨 Wing 的 Room 连接 | `auth-migration` 在 Kai 个人和 Driftwood 项目中自动关联 |
| **Closet** | 指向原始内容的摘要 | v3.0.0 为纯文本，未来使用 AAAK |
| **Drawer** | 原始 verbatim 全文 | 永不摘要，完整保留 |

**检索提升效果**（[官方测试](https://github.com/milla-jovovich/mempalace)）：
- 搜索全部 closets：60.9% R@10
- 限制在 wing 内：73.1%（+12%）
- wing + hall：84.8%（+24%）
- **wing + room**：94.8%（**+34%**）

### 2.2 AAAK：实验性缩写方言

AAAK（All-Ages Abbreviated Key-dialect）是 MemPalace 设计的压缩编码系统。

#### 当前状态（重要）

**官方更正声明**（[2026-04-07](https://github.com/milla-jovovich/mempalace#a-note-from-milla--ben--april-7-2026)）明确承认：
1. **AAAK 是有损缩写，不是无损压缩** — 无法从 AAAK 重建原文
2. **小文本不节省 token** — OpenAI tokenizer 实测：英文 66 tokens → AAAK 73 tokens
3. **AAAK 模式性能更低** — LongMemEval 84.2% vs Raw 模式 96.6%（-12.4 点）
4. **96.6% 的高分来自 Raw 模式，不是 AAAK**

#### AAAK 格式规范

```
Header: FILE_NUM|PRIMARY_ENTITY|DATE|TITLE
Zettel: ZID:ENTITIES|topic_keywords|"key_quote"|WEIGHT|EMOTIONS|FLAGS
Tunnel: T:ZID<->ZID|label
Arc:    ARC:emotion->emotion->emotion
```

**情感代码系统**（24 种）：
- `joy`（喜悦）、`fear`（恐惧）、`trust`（信任）
- `vul`（脆弱）、`rage`（愤怒）、`hope`（希望）等

**FLAGS 标记**：
- `ORIGIN` — 起源时刻
- `CORE` — 核心信念
- `DECISION` — 明确决策
- `PIVOT` — 情感转折点
- `TECHNICAL` — 技术细节

**适用场景**：大规模重复实体（如团队、项目名称重复数百次）场景下，实体代码摊销后可节省 token。

### 2.3 四层记忆栈（L0-L3）

MemPalace 采用渐进式记忆加载策略：

| 层级 | 名称 | 大小 | 加载时机 | 内容 |
|-----|------|-----|---------|------|
| **L0** | Identity | ~50 tokens | 始终加载 | `~/.mempalace/identity.txt` 用户定义的身份 |
| **L1** | Essential Story | ~120 tokens (AAAK) | 始终加载 | 高权重关键事实 |
| **L2** | Room Recall | 200-500 tokens | 按需 | 特定 wing/room 的最近会话 |
| **L3** | Deep Search | 无限制 | 显式查询 | 全量 ChromaDB 语义搜索 |

**成本对比**（基于 6 个月 AI 使用 = 19.5M tokens）：

| 方案 | Tokens 加载 | 年成本 |
|------|------------|--------|
| 粘贴全部历史 | 19.5M（不可行） | - |
| LLM 摘要 | ~650K | ~$507 |
| **MemPalace wake-up** | **~170** | **~$0.70** |
| MemPalace + 5 次搜索 | ~13,500 | ~$10 |

### 2.4 知识图谱：时态实体关系

使用 **SQLite**（本地）而非 Neo4j（云端）：

```python
from mempalace.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()
kg.add_triple("Kai", "works_on", "Orion", valid_from="2025-06-01")
kg.add_triple("Maya", "assigned_to", "auth-migration", valid_from="2026-01-15")

# 查询当前状态
kg.query_entity("Kai")
# → [Kai → works_on → Orion (current)]

# 查询历史状态（时间旅行）
kg.query_entity("Maya", as_of="2026-01-20")
# → [Maya → assigned_to → auth-migration (当时有效)]

# 使事实失效
kg.invalidate("Kai", "works_on", "Orion", ended="2026-03-01")
```

**与 Zep/Graphiti 对比**：

| 特性 | MemPalace | Zep |
|-----|-----------|-----|
| 存储 | SQLite（本地） | Neo4j（云端） |
| 成本 | 免费 | $25+/月 |
| 时态有效性 | ✅ | ✅ |
| 自托管 | 始终 | 仅企业版 |
| 隐私 | 完全本地 | SOC 2, HIPAA |

---

## 三、性能基准与争议

### 3.1 LongMemEval 基准测试

**官方成绩**：

| 模式 | R@5 | API 调用 | 备注 |
|------|-----|---------|------|
| **Raw** | **96.6%** | 0 | 最高零依赖得分 |
| Hybrid + Haiku rerank | 100% | ~500 | 可选方案 |
| AAAK | 84.2% | 0 | 有损压缩回归 |
| Rooms | 89.4% | 0 | Palace 结构 |

**可复现性**：
- [benchmarks/](https://github.com/milla-jovovich/mempalace/tree/main/benchmarks) 目录包含完整测试脚本
- Issue #39：[@gizmax](https://github.com/milla-jovovich/mempalace/issues/39) 在 M2 Ultra 上独立复现（< 5 分钟）

**与其他系统对比**（LongMemEval R@5）：

| 系统 | 成绩 | 需 API | 成本 |
|------|-----|--------|------|
| **MemPalace (hybrid)** | **100%** | 可选 | 免费 |
| Supermemory ASMR | ~99% | 是 | - |
| **MemPalace (raw)** | **96.6%** | **否** | **免费** |
| Mastra | 94.87% | 是 | API 费用 |
| Mem0 | ~85% | 是 | $19-249/月 |
| Zep | ~85% | 是 | $25+/月 |

### 3.2 官方更正声明（2026-04-07）

发布 48 小时内，社区发现宣传问题，作者发布[更正声明](https://github.com/milla-jovovich/mempalace#a-note-from-milla--ben--april-7-2026)：

#### 承认的问题

1. **AAAK token 计数错误**
   - 原使用启发式 `len(text)//3` 估算
   - 实测：英文 66 tokens → AAAK 73 tokens（反而增加）
   - AAAK 小文本不节省 token

2. **"30x lossless compression" 夸大**
   - AAAK 是有损缩写，非无损压缩
   - LongMemEval 84.2% vs 96.6%（-12.4 点）

3. **"+34% palace boost" 误导**
   - 实际是标准 ChromaDB 元数据过滤
   - 非创新检索机制

4. **矛盾检测未集成**
   - `fact_checker.py` 存在但未连接知识图谱

5. **"100% with Haiku rerank"**
   - 结果真实但未公开脚本
   - Hybrid v4 针对特定失败调优，清洁测试 98.4%

#### 修复计划

1. 重写 AAAK 示例，使用真实 tokenizer
2. 在 benchmark 文档中明确 mode 差异
3. 将 `fact_checker.py` 接入 KG
4. 修复 Issue #100（ChromaDB 版本）、#110（shell 注入）、#74（macOS segfault）

#### 社区反响

- 正面评价：作者快速响应、透明更正态度
- 感谢：@panuhorsmalahti、@lhl、@gizmax 等人的尖锐反馈
- 观点："我们宁愿正确而非 impress"

---

## 四、使用场景与集成

### 4.1 三种 Mining 模式

```bash
# 1. Projects 模式 —— 项目文件（代码、文档、笔记）
mempalace mine ~/projects/myapp

# 2. Convos 模式 —— 对话导出（Claude、ChatGPT、Slack）
mempalace mine ~/chats/ --mode convos

# 3. General 模式 —— 自动分类（决策、里程碑、问题）
mempalace mine ~/chats/ --mode convos --extract general
```

### 4.2 AI 工具集成

#### Claude Code（推荐）

```bash
# Marketplace 安装
claude plugin marketplace add milla-jovovich/mempalace
claude plugin install --scope user mempalace

# 重启后验证
/skills  # 应显示 "mempalace"
```

#### MCP 兼容工具（Claude、ChatGPT、Cursor、Gemini CLI）

```bash
# 连接 MemPalace
claude mcp add mempalace -- python -m mempalace.mcp_server

# 现在 AI 有 19 个工具可用
# 直接问："我们上个月关于 auth 做了什么决定？"
# Claude 自动调用 mempalse_search
```

**19 个 MCP 工具分类**：

| 类别 | 工具 | 功能 |
|------|------|------|
| Palace 读取 | `mempalace_status` | Palace 概览 + AAAK 规范 |
| | `mempalace_search` | 语义搜索（支持 wing/room 过滤） |
| | `mempalace_list_wings` | 列出所有 wings |
| Palace 写入 | `mempalace_add_drawer` | 添加 verbatim 内容 |
| 知识图谱 | `mempalace_kg_query` | 实体关系查询（支持时间过滤） |
| | `mempalace_kg_add` | 添加事实 |
| | `mempalace_kg_timeline` | 实体时间线 |
| 导航 | `mempalace_traverse` | 跨 wings 图遍历 |
| Agent Diary | `mempalace_diary_write` | 写入 AAAK 日记 |

#### 本地模型（Llama、Mistral）

```bash
# 1. Wake-up 命令 —— 加载关键事实到上下文
mempalace wake-up > context.txt
# 将 context.txt 粘贴到本地模型的 system prompt

# 2. CLI 搜索 —— 按需查询
mempalace search "auth decisions" > results.txt
# 将结果包含在 prompt 中
```

### 4.3 实际使用场景

#### 个人开发者跨项目管理

```bash
# 挖掘每个项目的对话记录
mempalace mine ~/chats/orion/ --mode convos --wing orion
mempalace mine ~/chats/nova/ --mode convos --wing nova

# 6 个月后查询："为什么我在这用了 Postgres？"
mempalace search "database decision" --wing orion
# → "选择 Postgres 而非 SQLite，因为 Orion 需要并发写入
#    且数据集将超过 10GB。决定时间：2025-11-03。"
```

#### 团队领导管理产品

```bash
# 挖掘 Slack 导出和 AI 对话
mempalace mine ~/exports/slack/ --mode convos --wing driftwood

# "Soren 上个 sprint 做了什么？"
mempalace search "Soren sprint" --wing driftwood
# → 14 个 closets：OAuth 重构、暗黑模式、组件库迁移

# "谁决定使用 Clerk？"
mempalace search "Clerk decision" --wing driftwood
# → "Kai 推荐 Clerk 而非 Auth0 —— 价格和开发者体验。
#    团队于 2026-01-15 同意。Maya 负责迁移。"
```

#### 专家 Agent 记忆管理

```bash
# 创建专家 agent
~/.mempalace/agents/
  ├── reviewer.json    # 代码质量、模式、bug
  ├── architect.json   # 设计决策、权衡
  └── ops.json         # 部署、事故、基础设施

# Agent 写入日记
mempalace_diary_write("reviewer",
    "PR#42|auth.bypass.found|missing.middleware.check|pattern:3rd.time.this.quarter|★★★★")

# Agent 读取历史
mempalace_diary_read("reviewer", last_n=10)
```

### 4.4 自动保存 Hooks

```json
{
  "hooks": {
    "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "/path/to/mempalace/hooks/mempal_save_hook.sh"}]}],
    "PreCompact": [{"matcher": "", "hooks": [{"type": "command", "command": "/path/to/mempalace/hooks/mempal_precompact_hook.sh"}]}]
  }
}
```

- **Save Hook**：每 15 条消息自动保存
- **PreCompact Hook**：上下文压缩前紧急保存

---

## 五、竞品对比分析

### 5.1 主流 AI 记忆系统对比

| 系统 | Stars | LongMemEval | 月费 | 存储 | 部署模式 | 特点 |
|------|-------|-------------|------|------|----------|------|
| **MemPalace** | 26.9k | **96.6%** | **$0** | SQLite | **纯本地** | Palace 结构、零 API |
| Mem0 | 52.3k | ~85% | $19-249 | 向量 DB | 托管/自托管 | 生态成熟、托管服务 |
| Zep | 4.4k | ~85% | $25+ | Neo4j | 云端 | 企业合规（SOC 2） |
| Mastra | 22.8k | 94.87% | $0 | LibSQL | 自托管 | 高性能、依赖 GPT API |
| Supermemory | 21.5k | ~99% | 按量 | 专有 | 云端 | 高准确率 |
| Letta | 11.3k | - | $20-200 | 本地文件 | 本地/托管 | Agent 专用记忆 |

### 5.2 差异化定位

**MemPalace 的独特价值**：
1. **唯一完全免费、零 API 依赖、纯本地**的方案
2. **Palace 结构** — 可解释的记忆地图，非黑盒向量检索
3. **信息零损失** — 存储 verbatim 全文，非 LLM 摘要
4. **极致隐私** — 数据永不离开本机

**适用场景建议**：
- **预算敏感/隐私优先** → MemPalace
- **追求最高性能** → Mastra (94.87%) 或 Supermemory (~99%)
- **企业合规** → Zep (SOC 2/HIPAA)
- **快速集成/成熟生态** → Mem0

### 5.3 技术路线对比

| 维度 | MemPalace | Mem0 | Zep |
|------|-----------|------|-----|
| 存储哲学 | 原始 verbatim | LLM 摘要 | 图谱+向量 |
| 架构 | 结构化 Palace | 分层记忆 | 时态知识图谱 |
| 检索 | 语义+元数据过滤 | 向量相似度 | 图谱遍历 |
| 压缩 | AAAK（有损实验性） | 自动摘要 | 原生存储 |
| 成本模型 | 零成本 | 订阅制 | 订阅制 |

---

## 六、风险与局限性

### 6.1 技术风险

1. **AAAK 压缩不成熟**
   - 有损压缩且性能更低（84.2% vs 96.6%）
   - 小文本反而增加 token 开销
   - 适用场景有限（大规模重复实体）

2. **矛盾检测未集成**
   - `fact_checker.py` 存在但孤立
   - 知识图谱无法自动检测冲突

3. **技术债务**
   - Issue #100：ChromaDB 版本需锁定
   - Issue #110：hooks 存在 shell 注入风险
   - Issue #74：macOS ARM64 segfault

### 6.2 项目风险

1. **宣传夸大后修复**
   - 发布初期过度宣传（"30x lossless"、"+34% boost"）
   - 虽快速更正，但影响公信力

2. **新项目管理风险**
   - 128 commits，单版本（v3.0.0）
   - 相比 Mem0（52.3k stars，2000+ commits）成熟度较低

3. **社区依赖**
   - 78 issues，112 PRs — 活跃但早期
   - 长期维护能力待观察

### 6.3 适用限制

- **非通用方案**：针对对话记忆优化，其他数据类型需适配
- **本地优先的代价**：无托管选项，需自行运维
- **学习曲线**：Palace 结构概念需理解

---

## 七、结论与建议

### 7.1 核心价值

MemPalace 是 AI 记忆系统领域的**重要实验**：

✅ **验证纯本地方案可行性** — 96.6% LongMemEval 成绩证明无需云端也能高性能  
✅ **探索结构化记忆** — Palace 架构为非黑盒记忆系统提供新思路  
✅ **极致成本优化** — $0.70/年 vs $507/年的对比令人印象深刻  
✅ **开源透明** — MIT 许可证、快速响应社区反馈

### 7.2 适用人群

**推荐使用**：
- 隐私敏感用户（数据不愿上云）
- 预算有限个人/小团队
- 技术爱好者（愿意实验新架构）
- 已有 Claude Code 工作流的用户

**不建议使用**：
- 追求开箱即用的非技术用户
- 需要企业级支持的场景
- 对稳定性要求极高的生产环境（目前为早期版本）

### 7.3 关键决策建议

| 需求 | 推荐方案 |
|------|----------|
| 纯本地 + 零成本 + 高隐私 | **MemPalace** |
| 成熟生态 + 托管服务 | Mem0 |
| 最高准确率（~99%） | Supermemory ASMR |
| 企业合规 + 支持 | Zep |
| 平衡性能与成本 | Mastra |

### 7.4 后续关注要点

1. **AAAK 迭代** — 是否能实现真正的 token 节省
2. **矛盾检测集成** — 知识图谱完整功能落地
3. **技术债务清理** — Issue #100、#110、#74 修复
4. **版本迭代** — 从 v3.0.0 到稳定版的演进

---

## 参考资源

- **GitHub 仓库**: https://github.com/milla-jovovich/mempalace
- **官方声明**: [Milla & Ben - April 7, 2026](https://github.com/milla-jovovich/mempalace#a-note-from-milla--ben--april-7-2026)
- **基准测试**: [benchmarks/BENCHMARKS.md](https://github.com/milla-jovovich/mempalace/blob/main/benchmarks/BENCHMARKS.md)
- **Discord 社区**: https://discord.com/invite/ycTQQCu6kn

---

**调研完成**: 2026-04-09  
**报告版本**: v1.0
