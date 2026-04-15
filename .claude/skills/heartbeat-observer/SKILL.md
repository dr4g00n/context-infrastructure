---
name: heartbeat-observer
description: 在 Claude Code 中直接执行 L1 AI Heartbeat Observer，扫描当日项目变动、按交通灯分类并追加写入 contexts/memory/OBSERVATIONS.md。适用场景：用户要求"run observer"、"daily observation"、"heartbeat observation" 或执行 periodic_jobs/ai_heartbeat/src/v0/observer.py 时。
---

# Skill: AI Heartbeat L1 Observer

## 目标

在 Claude Code 当前会话中完成每日观测记忆提取，将项目变动的认知信号分类为 🔴🟡🟢 三个持久化层级，并追加写入 `contexts/memory/OBSERVATIONS.md`。

## 核心约束（不可违背）

1. **幂等性**：在执行任何写入前，**必须先 Read `contexts/memory/OBSERVATIONS.md`**，检查是否已存在 `Date: YYYY-MM-DD` 条目。若存在，立即停止并回复「Entry for YYYY-MM-DD already exists, skipping」。
2. **角色隔离**：这是 L1 Observer 任务，**禁止修改 `rules/` 目录下的任何文件**。不要执行规则晋升或垃圾回收。
3. **路径规范**：结果中提到的任何文件或目录，**必须使用相对于项目根目录的完整路径**（例如 `journal/daily/2026-04-15.md`）。
4. **Append-only**：使用命令行追加（如 `echo -e "..." >> contexts/memory/OBSERVATIONS.md` 或 `tee -a`），禁止对大文件做全文重写。
5. **交通灯定义**：严格遵循以下分类标准（来自 SOP）：
   - **🔴 High**：跨项目通用的长效规律/方法论、硬性约束、影响系统架构的重大决策。
   - **🟡 Medium**：活跃项目的关键进展、未来几周内仍需参考的技术决策、局部架构变更。
   - **🟢 Low**：日常任务流水、瞬时 debug 记录、仅当天有效的临时上下文。

## 前置检查清单

- [ ] 已确定目标日期（默认：今天，YYYY-MM-DD 格式）
- [ ] 已完成幂等性检查
- [ ] 已读取 SOP：`periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`

## 执行步骤

### Step 1：加载上下文

使用 `Read` 读取以下文件，确保行为与项目哲学一致：
- `AGENTS.md`（工作区全局约束）
- `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`（SOP）
- `contexts/memory/OBSERVATIONS.md`（幂等性检查 + 近期历史上下文）

### Step 2：扫描变动

使用 `Bash` 运行 `find` 命令，扫描最近 24-48 小时内发生变动的关键目录。推荐命令示例：

```bash
find journal/daily contexts/thought_review contexts/survey_sessions adhoc_jobs rules contexts/memory \
  -type f -newer contexts/memory/OBSERVATIONS.md \
  ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" ! -path "*/.venv/*" ! -path "*/venv/*" ! -path "*/target/debug/*" ! -path "*/.claude/*"
```

**扫描重点目录**：
- `journal/daily/` — 每日工作总结与次日规划
- `contexts/thought_review/` — 深度思考与洞察
- `contexts/survey_sessions/` — 调研报告
- `adhoc_jobs/` — 临时项目进展
- `rules/` — 规则与 skill 的新增/变更（仅观测，不修改）
- `contexts/memory/PENDING_RULES_PROPOSALS.md` — 待处理的规则提案

**忽略黑名单**：
- `contexts/daily_records/`（机械重复性数据）
- `contexts/blog/content/` 中的旧文章（除非 frontmatter 的 `Date` 与目标日期匹配）
- 所有缓存、构建产物、隐藏目录（`.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `target/debug/` 等）

### Step 3：读取与过滤

对 Step 2 发现的候选文件，使用 `Read` 检查内容：
- **Blog 内容**：若路径在 `contexts/blog/content/`，必须读取 Markdown frontmatter 中的 `Date` 字段。仅当 `Date` 为目标日期时才记录；否则视为格式重排导致的旧文章误报，直接丢弃。
- **机械噪音**：排除纯 lockfile 更新、缓存文件变动、无语义意义的自动格式化。

### Step 4：分类

基于 SOP 的交通灯定义，对过滤后的信号进行认知分级。如果某条信息在未来 3 个月内不会产生复用价值，果断丢弃。

### Step 5：格式化

构造如下观测块（每条记录单行化，来源使用相对路径）：

```
Date: YYYY-MM-DD

🔴 High: [分类] 描述。来源: relative/path/to/file.md
🟡 Medium: [分类] 描述。来源: relative/path/to/file.md
🟢 Low: [分类] 描述。来源: relative/path/to/file.md
```

若某一层级无条目，可省略该行。

### Step 6：追加写入

使用 `Bash` 追加到目标文件：

```bash
echo -e "Date: 2026-04-15\n\n🔴 High: ...\n🟡 Medium: ...\n🟢 Low: ...\n" >> contexts/memory/OBSERVATIONS.md
```

### Step 7：汇报

完成后在 chat 中输出简短 Walkthrough：
- 扫描了哪些区域
- 过滤掉了多少噪音
- 产出了几条 🔴/🟡/🟢 记录
- 确认追加写入成功
