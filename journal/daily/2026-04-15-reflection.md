# 次日行动清单 + 代码指针 - 2026-04-15

> 基于今日工作摘要生成的明日开工文档，直接可用。

---

## 明日任务清单

### P0 - 建立测试框架（最高优先级）

- [ ] **1. 为 analyze_transcript.py 编写单元测试**
  - **入口文件**：`~/.claude/hooks/rules_evolution/analyze_transcript.py`
  - **测试目标**：覆盖 4 种触发条件的正则匹配逻辑，确保硬触发（条件 1、2 前半）零误报
  - **测试文件建议位置**：`~/.claude/hooks/rules_evolution/tests/test_analyze_transcript.py`
  - **验证标准**：
    - 输入包含"你违背了 SOUL.md" → 必须触发条件 1
    - 输入包含"同一类错误"+次数描述 → 必须触发条件 2
    - 输入包含"原则问题""规则定义不够强" → 必须触发条件 3
    - 正常技术讨论（不含触发词）→ 必须不触发

- [ ] **2. 设计软触发测试用例集**
  - **入口文件**：`~/.claude/hooks/rules_evolution/analyze_transcript.py` + `rules/CLAUDE.md`
  - **测试目标**：验证 AI 在会话中能否正确识别"同一错误 2+ 次"和"自我定义与行为不一致"
  - **测试文件建议位置**：`~/.claude/hooks/rules_evolution/tests/test_soft_triggers.md`
  - **验证标准**：
    - 构造 3 组模拟对话，每组包含隐式软触发信号
    - 手动运行 analyze_transcript.py 或让 AI 自检，确认至少 80% 被识别
    - 记录漏识别的 case，用于优化正则或补充语义提示词

- [ ] **3. 验证 stop_hook_wrapper.sh 串联逻辑**
  - **入口文件**：`~/.claude/hooks/stop_hook_wrapper.sh`
  - **测试目标**：MemPalace save hook 与规则进化 hook 按顺序执行，错误不互相吞没
  - **验证标准**：
    - 手动触发一次会话结束，检查 `~/.claude/hook_state/rules_evolution/hook.log` 有本次执行记录
    - 检查 MemPalace 正常保存（无丢失）
    - 若 wrapper 返回非 0，Claude Code 能正确感知

### P1 - 验证防循环机制

- [ ] **4. 测试单会话上限与全局冷却**
  - **入口文件**：`~/.claude/hooks/rules_evolution/rules_evolution_stop_hook.sh`
  - **状态目录**：`~/.claude/hook_state/rules_evolution/`
  - **验证标准**：
    - 同一会话内触发 2 次硬触发，第二次被跳过（单会话上限 1 次）
    - 30 分钟内再次触发，被冷却机制拦截
    - 冷却结束后正常触发
    - 检查 `trigger_history.jsonl` 和冷却时间戳文件状态一致

- [ ] **5. 验证待提案去重逻辑**
  - **入口文件**：`~/.claude/hooks/rules_evolution/rules_evolution_stop_hook.sh`
  - **输出文件**：`/Users/dr4/WorkSpace/context-infrastructure/contexts/memory/PENDING_RULES_PROPOSALS.md`
  - **验证标准**：
    - 同一触发内容在 30 分钟内不生成重复提案
    - 不同触发内容生成独立提案条目

### P2 - 文档与规则完善

- [ ] **6. 更新规则进化 README**
  - **入口文件**：`~/.claude/hooks/rules_evolution/README.md`
  - **内容**：补充测试框架说明、软触发识别策略、已知限制

- [ ] **7. 检视 rules/ 目录是否需要首轮进化**
  - **入口目录**：`/Users/dr4/WorkSpace/context-infrastructure/rules/`
  - **动作**：若测试中发现规则表述歧义，按进化流程生成提案

---

## 快速代码指针

| 作用 | 绝对路径 |
|------|----------|
| Hooks 串联入口 | `~/.claude/hooks/stop_hook_wrapper.sh` |
| 规则进化主入口 | `~/.claude/hooks/rules_evolution/rules_evolution_stop_hook.sh` |
| Transcript 分析脚本 | `~/.claude/hooks/rules_evolution/analyze_transcript.py` |
| Hook 文档 | `~/.claude/hooks/rules_evolution/README.md` |
| Hook 运行状态 | `~/.claude/hook_state/rules_evolution/hook.log` |
| 触发历史记录 | `~/.claude/hook_state/rules_evolution/trigger_history.jsonl` |
| 冷却时间戳 | `~/.claude/hook_state/rules_evolution/.cooldown_until` |
| 单会话触发标记 | `~/.claude/hook_state/rules_evolution/.session_triggered` |
| Workspace 权限配置 | `/Users/dr4/WorkSpace/context-infrastructure/.claude/settings.local.json` |
| 待处理规则提案 | `/Users/dr4/WorkSpace/context-infrastructure/contexts/memory/PENDING_RULES_PROPOSALS.md` |
| 被进化的规则目录 | `/Users/dr4/WorkSpace/context-infrastructure/rules/` |

---

## 明日起手式

1. 先读 `~/.claude/hooks/rules_evolution/analyze_transcript.py`，理解当前正则模式
2. 在 `~/.claude/hooks/rules_evolution/tests/` 创建测试文件
3. 跑一轮硬触发单元测试，修复误报/漏报
4. 再测防循环机制（可手动构造 transcript 片段）
5. 最后处理软触发测试用例
