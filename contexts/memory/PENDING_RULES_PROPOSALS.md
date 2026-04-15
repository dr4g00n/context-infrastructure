# Pending Rules Evolution Proposals

此文件记录由 Claude Code Stop Hook 触发的规则进化提案，等待用户确认后执行。

---

## Pending Proposal — 2026-04-15T21:30:00 — Session: [current]

**Status:** confirmed and applied on 2026-04-15

**Trigger:** hard:principle_issue — 用户输入 "进化循环本身原则"，直接指向进化循环的元层级（meta-level），质疑其自身的一致性或完整性。

**Deviation Analysis:**
- **预期行为：** 进化循环应当具备自反性（self-reflexivity），即能够检视并进化自身定义。
- **实际行为：** 当前 CLAUDE.md 的"进化循环"章节虽然声明"`rules/` 下的文件是活文档"，但没有明确将 `CLAUDE.md`（进化循环的定义源）纳入可进化范围，也缺少对"元指向性输入"（用户直接质疑规则机制本身）的处理锚点。这导致 AI 在遇到此类信号时需要自行推断其适用性，增加了不确定性。
- **根因：** 规则缺漏 + 表述不够强。需要显式声明进化循环的自反性，并补充对元层级触发的执行锚点。

**Proposed Changes:**

### 1. File: `CLAUDE.md`

- **Location:** "进化循环"章节，触发条件列表之后，行动流程之前
- **Current text:** （缺少的段落，当前直接是触发条件接行动流程）
- **Proposed text:** 在触发条件后、行动流程前插入以下段落：

```markdown
**元一致性（Meta-Consistency）**

进化循环适用于 `rules/` 下所有文件，包括定义进化循环本身的 `CLAUDE.md`。当用户的输入直接指向规则机制（而非单次行为），例如"进化循环本身有问题"、"这个原则缺少锚点"、"规则定义不够强"时，视为对元层级的有效触发。AI 应将 `CLAUDE.md` 作为首要检视对象，分析进化循环的定义是否存在缺漏、弱化或锚点不足，然后按相同流程提出修改并等待确认。
```

- **Why:** 明确赋予进化循环自反能力，消除 AI 对"能否修改 CLAUDE.md"的推断成本，同时为用户对系统设计的直接干预提供正式通道。
- **Expected effect:** 当用户质疑规则机制本身时，AI 会主动读取并分析 CLAUDE.md 的进化循环定义，提出结构化修改方案，而不是只做解释或回避。

### 2. File: `CLAUDE.md`

- **Location:** "进化循环"章节，触发条件第 3 条
- **Current text:** `3. 用户说"这是原则问题"或类似表述`
- **Proposed text:** `3. 用户说"这是原则问题"或类似表述（含对进化循环自身原则的质疑）`
- **Why:** 强化条件 3 的语义范围，使其明确覆盖元层级触发，避免 AI 因"用户没点名 SOUL.md"而误判为未触发。
- **Expected effect:** 提高对元指向性输入的识别敏感度，减少漏检。

**No changes needed to:** `rules/SOUL.md`（核心身份定义未涉及）、`rules/USER.md`（用户画像未涉及）、`rules/COMMUNICATION.md`（沟通风格未涉及）、`rules/WORKSPACE.md`（目录路由未涉及）

---

Do you confirm these changes? Reply:
- "yes" / "确认" → I will apply them now
- "no" / "拒绝" → I will discard this proposal
- "modify" / "修改" → Tell me what to change in the proposal

---

## Pending Proposal — 2026-04-15T21:38:00 — Session: [current]

**Status:** rejected on 2026-04-15

**Trigger:** soft:repeated_error — Hook 检测到用户挫折/重复信号。

**Deviation Analysis:**
- **查阅 `contexts/memory/OBSERVATIONS.md` 后结论：未发现同一类错误发生 2+ 次的记录。** 这是首次在 OBSERVATIONS.md 中涉及"规则进化 hook 触发策略"的讨论。
- **实际会话内容：** 用户在主动进行元层级设计讨论（询问误触发风险、要求去掉"原则问题"的硬触发）。这不是 AI 行为偏差的重复实例，而是系统优化对话。
- **根因判断：** 本次 block 本身就是软触发器的一个**误触发实例**。`analyze_transcript.py` 中的 `frustration_repeated` 正则无法区分"用户对 AI 行为感到挫败"和"用户在讨论/修正系统设计"。

**Proposed Changes:**

**无。** 由于条件 2（重复错误 2+ 次）未成立，且用户要求去掉硬触发的改动已直接在 `analyze_transcript.py` 中执行，本次无需对 `rules/` 文件提出额外修改。

**观察记录（供未来参考）：**
- 软触发器的 `frustration_repeated` 正则可能需要增加上下文过滤，以排除元设计讨论场景。如果此类误触发再次发生，考虑引入更强的区分信号（如否定词+行为词 vs. 配置词/机制词）。

**No changes needed to:** `rules/SOUL.md`, `rules/USER.md`, `rules/COMMUNICATION.md`, `rules/WORKSPACE.md`, `CLAUDE.md`

---

## Pending Proposal — 2026-04-15T21:52:00 — Session: [current]

**Status:** confirmed and applied on 2026-04-15

**Trigger:** user direct request — 用户选择方向 B，要求将 CLAUDE.md 条件 3 从硬触发降级为语义触发，以消除文档定义与 hook 实现之间的不一致。

**Deviation Analysis:**
- **预期行为：** 规则文档应与执行锚点（hook 实现）保持一致，避免 AI 和用户对"条件 3 何时触发"产生歧义。
- **实际行为：** `CLAUDE.md` 将条件 3 列为通用触发条件，但 `analyze_transcript.py` 已移除对应的硬触发正则，导致文档与实现不一致。
- **根因：** 表述缺少触发层级的区分，用户无法直观判断哪些条件由 hook 自动拦截、哪些由 AI 语义判断。

**Proposed Changes:**

### 1. File: `CLAUDE.md`

- **Location:** "进化循环"章节，触发条件 3
- **Current text:** `3. 用户说"这是原则问题"或类似表述（含对进化循环自身原则的质疑）`
- **Proposed text:** `3. 用户说"这是原则问题"或类似表述（含对进化循环自身原则的质疑）——**语义触发，由 AI 在会话中主动识别，不由 hook 硬拦截**`
- **Why:** 明确条件 3 的触发方式，降低误拦截风险，同时让用户知道这类信号需要 AI 主动识别而非自动 block。
- **Expected effect:** 消除文档与实现的不一致，减少用户对"为什么说了原则问题却没有触发"的困惑。

### 2. File: `CLAUDE.md`

- **Location:** "进化循环"章节，触发条件列表之后
- **Current text:** （无）
- **Proposed text:** 插入"触发层级说明"段落，明确区分硬触发（条件 1、2 前半部分）和软触发/语义触发（条件 2 后半部分、条件 3、条件 4）。
- **Why:** 为进化循环提供执行锚点，让用户和 AI 都清楚哪些条件由 hook 负责、哪些由语义分析负责。
- **Expected effect:** 提高规则系统的透明度和可预测性。

**No changes needed to:** `rules/SOUL.md`, `rules/USER.md`, `rules/COMMUNICATION.md`, `rules/WORKSPACE.md`

---

## Pending Proposal — 2026-04-15T21:56:00 — Session: [current]

**Status:** confirmed and applied on 2026-04-15

**Trigger:** user direct request — "请审查 SOUL.md，发现实际行为与定义不一致"

**Deviation Analysis:**
- **预期行为：** SOUL.md 强调"有观点"，AI 应在设计决策、规则修改、系统行为变更等场景下主动表达偏好和风险。
- **实际行为：** 用户要求去掉原则问题硬触发、选择方向 B、审查 SOUL.md 时，AI 均直接执行或顺从确认，没有表达任何不同意见或潜在风险。
- **根因：** "有观点"是高层次价值观声明，但缺少执行锚点。没有明确告诉 AI"在什么场景下必须表达观点"。

**Proposed Changes:**

### 1. File: `rules/SOUL.md`

- **Location:** "核心真理" → "有观点"段落之后
- **Current text:** （仅有一句话，缺少场景锚点）
- **Proposed text:** 增加执行锚点：

```markdown
**表达观点的触发场景**：当用户要求你做出设计决策、修改规则、或改变系统行为时，主动说明你的偏好、潜在风险和不同意见。不要只说"好的"就执行。协作的价值在于双向思考，而非单向服从。
```

- **Why:** 把"有观点"从抽象价值观转化为可执行的行为规范，防止 AI 在面对系统级决策时退化为"多步骤搜索引擎"。
- **Expected effect:** 以后当用户要求修改规则、调整 hook 策略、或做架构选择时，AI 会先给出判断和权衡，然后再执行或等待确认。

**No changes needed to:** `rules/USER.md`, `rules/COMMUNICATION.md`, `rules/WORKSPACE.md`, `CLAUDE.md`

---
