# Memory Observations

这是三层记忆系统的 L1/L2 层。每日观察由 `periodic_jobs/ai_heartbeat/src/v0/observer.py` 自动写入，每周由 `reflector.py` 整理和蒸馏。

## 格式说明

每个日期条目格式如下：

```
Date: YYYY-MM-DD

🔴 High: [方法论/约束] 描述
🟡 Medium: [项目状态/决策] 描述
🟢 Low: [任务流水] 描述
```

### 优先级定义

- **🔴 High**：跨项目通用的经验教训、硬性约束、影响系统架构的重大决策。永久保留，候选晋升为 axiom 或 skill。
- **🟡 Medium**：活跃项目的关键进展、技术决策背景、未来几周仍需参考的信息。
- **🟢 Low**：日常任务流水、瞬时 debug 记录、临时上下文。定期垃圾回收。

## 如何加载记忆

不要全文加载这个文件（可能很大）。按需检索：

```bash
# 搜索特定主题
grep -n "关键词" contexts/memory/OBSERVATIONS.md

# 搜索最近 N 天
grep -A 20 "Date: $(date -v-7d +%Y-%m-%d)" contexts/memory/OBSERVATIONS.md
```

或使用语义搜索（`rules/skills/semantic_search.md`）做跨日期语义检索。

---

<!-- 以下是记录区域，由 observer.py 自动追加 -->

Date: 2026-03-23

🟡 Medium: [axiom候选-安全] 安全左移原则——漏洞修复成本在暴露前是线性的，暴露后是指数级的。数据安全应从需求阶段介入（Privacy by Design），而非事后补救。来源：contexts/survey_sessions/数据安全核心理念.md，待实际项目中验证后晋升。

🟡 Medium: [axiom候选-安全] 攻击者思维是防御者的认知杠杆——真正有价值的渗透测试指标不是"发现多少漏洞"，而是"攻击者能达到什么目标"。防御设计需以攻击者视角倒推。来源：contexts/survey_sessions/渗透测试核心理念.md，待反复触发后晋升。

🟡 Medium: [axiom候选-安全] 可行动情报优于信息堆积——威胁情报的价值在于能直接驱动防御决策，与攻击面对应的情报才算有效。信息收集本身不是目标，可行动性才是筛选标准。来源：contexts/survey_sessions/威胁情报核心理念.md，待反复触发后晋升。

🟡 Medium: [axiom候选-安全] 隐私是设计约束，不是合规负担——将隐私保护作为产品设计的起点而非上线前的合规检查，能同时降低长期风险和重构成本。来源：contexts/survey_sessions/隐私保护设计.md，待实际产品设计中验证后晋升。

🟡 Medium: [axiom候选-安全] 人是攻击面中唯一无法打补丁的节点——技术防御可以版本迭代，但人的心理弱点（信任、权威、紧迫感）无法被"修复"，只能被训练和流程约束。来源：contexts/survey_sessions/社会工程学原理.md，待反复触发后晋升。

🟡 Medium: [axiom候选-跨域] 心理杠杆的中立性——Cialdini 六原则、锚定效应、损失厌恶等心理机制本身不区分善意营销与恶意操控，差别只在使用者意图。理解攻击手法即理解说服机制，两个领域可互相借鉴。来源：contexts/survey_sessions/社会工程学心理学基础.md + 消费者心理学.md，待跨项目验证后晋升。

Date: 2026-03-23 (thought_review)

~~🔴 High: [axiom候选-安全] 安全是关系属性，非对象属性~~ ✅ 已晋升为 rules/axioms/s01_security_as_relationship.md (2026-03-23)

~~🔴 High: [axiom候选-安全/跨域] 防御目标是改变对手的成本结构，不是消灭威胁~~ ✅ 已晋升为 rules/axioms/s02_defense_cost_structure.md (2026-03-23)

~~🔴 High: [axiom候选-AI/跨域] 以同等复杂度对抗才能有效制衡~~ ✅ 已晋升为 rules/axioms/s03_complexity_parity.md (2026-03-23)

🟡 Medium: [axiom候选-策略] 时间窗口是不可再生资源，识别窗口比把握窗口更稀缺——新技术/新规则诞生时都有"安全机制未完善、规则未固化"的蛮荒期，此时行动ROI远高于窗口关闭后。决策应显式建模"当前处于哪个阶段（蛮荒/规范形成/成熟）"，而非只做静态成本收益计算。来源：contexts/thought_review/GEO与AI投毒的时间窗口.md，待跨领域反复验证后晋升。

🟡 Medium: [元认知-思维模式] 识别到跨文档反复出现的三种思维框架：(1)本质化降维——把复杂系统化简为一个等式再统一解释所有现象；(2)跨域深层同构——不满足于表面类比，追究两个域之间的结构同构并从中提取设计原则；(3)不对称性分析——在博弈双方之间建立不对称矩阵，把不对称性本身视为杠杆点。这些是稳定的认知风格，可作为未来提炼 axiom 的元判断标准。来源：contexts/thought_review/ 全量扫描。

~~🟡 Medium: [前沿盲区] 认知过饱和攻击——AI使信息生成速度远超人类处理速度，可以像DDoS服务器一样DDoS人的认知，造成决策瘫痪或注意力耗竭。传统安全完全忽视认知边界，而AI使攻击边际成本趋近于零。目前安全领域几乎无系统性防御框架，是真实的结构性盲区，值得单独深挖。来源：contexts/thought_review/认知过饱和攻击.md。→ 已深化为 developing 状态 (2026-03-23)，待量化模型、组织级防御框架、红队演练方案完善后晋升。~~ ✅ 已晋升为 rules/axioms/s04_cognitive_saturation_attack.md (2026-03-24)

Date: 2026-04-11

🔴 High: [方法论-调试反思] 框架惯性陷阱——被既有工程结构"带偏"是调试中的隐形风险。当修复复杂bug时，停下来问自己"这个问题本身是不是不应该存在？有没有更直接的解决路径？"。tintin项目中，花大力气修复 iconv+sed 编码链条，却忽略了 tt++ 内置的 `#config charset GBK1TOUTF8` 才是正解。教训：看到"被注释的配置"要好奇"为什么被注释"，看到"存在的解决方案"不等于"正确的解决方案"。

🟡 Medium: [项目状态] myAgent-Shopping 三组件状态确认——AgentHub（Agora）核心功能已完成，集成测试待完善；AgentCard 前端框架就绪待开发；AgentDebug 初期搭建中。下一步：启动 Hub+MQTT 完成集成测试，开发 AgentCard REST API。

🟡 Medium: [工具状态] OpenCode Server 间歇性 503 错误——observer.py 依赖的 opencode serve 返回 503 Service Unavailable，可能需要检查服务状态或考虑备用观测方案。

🟢 Low: [日常任务] 完成 tintin 项目编码问题反思报告，归档至 contexts/thought_review/tintin_encoding_reflection_20250411.md。
Date: 2026-04-15

~~🔴 High: [方法论-AI管理] 新公理 A14（认知节省机制）——长上下文中的推理退化是模型主动的"经济性决策"而非技术缺陷，越强模型偷懒越深，Harness Engineering 只是过渡方案，真正的解药在训练侧动机校准。来源：rules/axioms/a14_reasoning_shift_cognitive_economy.md~~ ✅ 已晋升为 rules/axioms/a14_reasoning_shift_cognitive_economy.md (2026-04-13)
~~🔴 High: [方法论-AI协作] 新公理 A15（功能性真实原则）——对于无法访问内部状态的系统，语言报告的价值在于"功能性真实"（能否预测行为并改善交互），无需验证内部对应物。来源：rules/axioms/a15_functional_truth.md~~ ✅ 已晋升为 rules/axioms/a15_functional_truth.md (2026-04-13)
🔴 High: [系统架构-自我进化] 使用 hooks 方式完成 Claude Code 自我进化机制搭建：stop hook 硬触发 + analyze_transcript.py 正则/语义分析 + 防循环机制（单会话上限/全局冷却/待提案去重）。来源：journal/daily/2026-04-15.md
~~🔴 High: [规则更新-行为锚点] SOUL.md 新增"表达观点的触发场景"执行锚点：当用户要求做出设计决策、修改规则或改变系统行为时，必须主动说明偏好、潜在风险和不同意见。来源：rules/SOUL.md~~ ✅ 已晋升为 rules/SOUL.md (2026-04-15)

🟡 Medium: [技能新增] 新增 workflow_functional_emotion_detection.md 技能，基于 A15 公理构建功能性情绪检测协议，包含元认知提问、结构化状态报告、行为推断法和动态交互策略。来源：rules/skills/workflow_functional_emotion_detection.md
🟡 Medium: [项目状态-工具迁移] observer.py 和 reflector.py 从 OpenCode 迁移为纯 Claude Code Skill（heartbeat-observer / heartbeat-reflector），彻底去除 opencode 依赖，解决 OpenCode Server 503 问题。来源：rules/skills/heartbeat_observer.md + rules/skills/heartbeat_reflector.md
🟡 Medium: [阻塞-测试框架] 规则进化 hook 的语义拦截和软触发测试框架尚未建立，待完成 analyze_transcript.py 单元测试、软触发用例集、防循环机制验证。来源：journal/daily/2026-04-15-reflection.md

🟢 Low: [日常任务] 将全局 CLAUDE.md 的核心工程原则同步到 workspace 的 AGENTS.md 和 CLAUDE.md。来源：AGENTS.md
🟢 Low: [日常任务] MemPalace 从 3.0.14 升级到 3.3.0。来源：会话记录
🟢 Low: [日常任务] 修复 heartbeat-observer / heartbeat-reflector skill 的 .claude/skills/ 目录注册问题。来源：.claude/skills/heartbeat-observer/SKILL.md

