---
name: heartbeat-reflector
description: 在 Claude Code 中直接执行 L2 AI Heartbeat Reflector，分析 contexts/memory/OBSERVATIONS.md 中的 🔴/🟡 条目，生成规则晋升提案追加到 PENDING_RULES_PROPOSALS.md，经用户确认后执行 rules/ 修改和 OBSERVATIONS.md 垃圾回收。适用场景：用户要求 "run reflector"、"weekly reflection"、"heartbeat reflector" 或执行 periodic_jobs/ai_heartbeat/src/v0/reflector.py 时。
---

# Skill: AI Heartbeat L2 Reflector

## 目标

在 Claude Code 当前会话中完成 L2 反思与晋升任务：将 L1 观测中的长效信号提炼为结构化规则晋升提案，**经用户确认后**执行 `rules/` 修改和 `OBSERVATIONS.md` 垃圾回收。

## 核心约束（不可违背）

1. **未经用户明确确认（"yes"/"确认"/"apply"），禁止修改任何 `rules/` 下的文件**。这是 `CLAUDE.md` 进化循环的硬性要求。
2. **角色隔离**：这是 L2 Reflector，只负责规则晋升和 GC；不要混淆为 L1 Observer（不要再扫描当日新变动）。
3. **提案持久化**：所有规则修改意图必须先以结构化格式追加到 `contexts/memory/PENDING_RULES_PROPOSALS.md`。
4. **晋升门槛**：只有满足"跨项目通用 + 多次验证 + 有明确适用场景"的观测点才值得晋升。
5. **GC 范围**：仅对已晋升条目做删除线标记，以及清理超过 30 天且无后续引用的 🟢 记录。不要删除尚未处理的 🔴/🟡 内容。

## 前置检查清单

- [ ] 已读取 `AGENTS.md` 和 `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`
- [ ] 已读取 `contexts/memory/OBSERVATIONS.md`
- [ ] 已理解当前工作区 `CLAUDE.md` 中"进化循环"的确认要求

---

## Phase 1: 分析与提案

### Step 1: 加载上下文

使用 `Read` 读取：
- `AGENTS.md`
- `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`
- `contexts/memory/OBSERVATIONS.md`
- `contexts/memory/PENDING_RULES_PROPOSALS.md`（了解现有提案格式）

### Step 2: 筛选候选条目

从 `OBSERVATIONS.md` 中提取：
- 所有 **🔴 High** 条目
- 近期（30 天内）的 **🟡 Medium** 高优条目

**跳过**已经处理的内容：
- 带有 `~~删除线~~ ✅ 已晋升` 的条目
- 已明确标记为废弃或过时的条目

### Step 3: 职责归类

对每个候选观测点，判断其最适配的目标规则文件：

| 目标文件 | 职责边界 |
|----------|----------|
| `rules/SOUL.md` | Agent 身份、核心价值观、行为底线 |
| `rules/USER.md` | 用户画像、人生哲学、长期目标 |
| `rules/COMMUNICATION.md` | 沟通风格、表达偏好（仅限沟通，不含技术知识） |
| `rules/WORKSPACE.md` | 目录路由、文件索引 |
| `rules/skills/` | 技术方法论、工作流、最佳实践 |
| `rules/axioms/` | 跨域通用决策原则、认知公理 |
| `CLAUDE.md` | 工作区级别的进化循环、元机制定义 |

如果某个观测点不符合以上任何职责边界，或未达到晋升门槛，**果断丢弃**。

### Step 4: 生成结构化提案

构造与现有 `PENDING_RULES_PROPOSALS.md` 格式一致的提案块，使用 `Bash` 追加到文件末尾。格式模板：

```markdown
---

## Pending Proposal — YYYY-MM-DDTHH:MM:SS — Session: [current]

**Status:** pending review

**Trigger:** heartbeat-reflector — L2 周期性反思，将 🔴/🟡 观测点晋升到规则层。

**Deviation Analysis:**
- **预期行为：** ...
- **实际行为/观测来源：** ...（引用 OBSERVATIONS.md 中的具体条目）
- **根因：** 规则缺漏 / 表述不够强 / 缺乏执行锚点

**Proposed Changes:**

### 1. File: `rules/TARGET.md`

- **Location:** 章节/段落
- **Current text:** ...
- **Proposed text:** ...
- **Why:** ...
- **Expected effect:** ...

**No changes needed to:** ...（列出未涉及的规则文件）

---

Do you confirm these changes? Reply:
- "yes" / "确认" → I will apply them now
- "no" / "拒绝" → I will discard this proposal
- "modify" / "修改" → Tell me what to change in the proposal
```

追加命令示例：
```bash
cat << 'EOF' >> contexts/memory/PENDING_RULES_PROPOSALS.md

[PASTE PROPOSAL BLOCK HERE]
EOF
```

### Step 5: 向用户汇报并等待确认

在 chat 中输出：
- 本次分析覆盖了多少条 🔴/🟡 记录
- 筛选后保留了多少个候选
- 生成了几份提案、涉及哪些目标文件
- 每份提案的核心改动一句话摘要

然后**主动声明**：
> 以上提案已追加到 `contexts/memory/PENDING_RULES_PROPOSALS.md`。请回复 **"yes" / "确认"** 以执行 `rules/` 修改和 OBSERVATIONS.md 垃圾回收；回复 **"no" / "拒绝"** 则跳过本次晋升；也可以告诉我需要修改提案的哪一部分。

**停止执行任何文件修改，等待用户输入。**

---

## Phase 2: 执行晋升（仅在用户确认后）

如果用户回复 "yes"/"确认"/"apply"：

### Step 6: 修改规则文件

按提案内容逐条修改 `rules/` 下目标文件。使用 `Edit` 工具进行精确替换，避免全文重写。

### Step 7: OBSERVATIONS.md GC

1. **标记已晋升条目**：对已晋升的观测条目，在 `OBSERVATIONS.md` 中将其标记为删除线并附加晋升记录：
   ```markdown
   ~~🔴 High: [分类] 描述。来源: ...~~ ✅ 已晋升为 rules/axioms/a01_xxx.md (YYYY-MM-DD)
   ```
2. **清理过期 🟢 记录**：删除超过 30 天且无后续引用的 🟢 Low 记录。

### Step 8: 更新提案状态

在 `PENDING_RULES_PROPOSALS.md` 中，将本次已执行提案的 `**Status:** pending review` 更新为：
```markdown
**Status:** confirmed and applied on YYYY-MM-DD
```

### Step 9: 汇报

输出简短 Walkthrough：
- 哪些观测点被晋升到了哪个规则文件
- GC 了多少条记录
- 哪些提案被拒绝或待修改（如果有）

---

## 如果用户回复 "no" / "拒绝"

1. 不修改任何 `rules/` 文件
2. 不执行 GC
3. 在 `PENDING_RULES_PROPOSALS.md` 中将对应提案的 Status 更新为 `rejected on YYYY-MM-DD`
4. 简短回复："已跳过本次晋升，提案状态已更新。"
