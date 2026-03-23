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

🟡 Medium: [前沿盲区] 认知过饱和攻击——AI使信息生成速度远超人类处理速度，可以像DDoS服务器一样DDoS人的认知，造成决策瘫痪或注意力耗竭。传统安全完全忽视认知边界，而AI使攻击边际成本趋近于零。目前安全领域几乎无系统性防御框架，是真实的结构性盲区，值得单独深挖。来源：contexts/thought_review/认知过饱和攻击.md。→ 已深化为 developing 状态 (2026-03-23)，待量化模型、组织级防御框架、红队演练方案完善后晋升。
