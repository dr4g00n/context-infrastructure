---
title: "Share Your Projects"
source: "https://www.superlinear.academy/c/ai-resources/ai-mastery"
author:
  - "[[立正Admin👀1d]]"
  - "[[脆花💙6h]]"
published:
created: 2026-04-12
description: "Explore Share Your Projects space in Superlinear Academy"
tags:
  - "clippings"
---
两年的AI培训经验告诉我们：AI 不靠谱，几乎从来不是工具本身的问题，而是人的问题。

## TLDR

- 顶尖 AI 用户（以下称为AI Builders）和普通人之间存在五条可量化的技术差距，不是天赋，是方法
- 差距 1： **产出能不能直接用** ——靠的是 Document-First 和 Context Curation，不是更好的 prompt
- 差距 2： **能不能诊断 AI 为什么出错** ——hallucination、context 饱和、指令歧义是三类根因，修法完全不同
- 差距 3： **能不能把完整任务 delegate 给 AI** ——搭建 Agentic Loop，一人驱动多个 agent 并行
- 差距 4： **使用经验能不能变成团队资产** ——Context Architecture + MEMORY.md 让系统越跑越强
- 差距 5： **AI 从执行工具变成思考伙伴** ——前四条做好之后，context 积累到密度时自然涌现

## 正文

我们经常听到这样的抱怨：AI 生成的内容根本没法直接用、让它写代码老是出错、我试过，不靠谱。

与此同时，另一个世界正在悄悄发生。

> *"For me personally, it has been 100% for two+ months now, I don't even make small edits by hand. I shipped 22 PRs yesterday and 27 the day before, each one 100% written by Claude."*

— Boris Cherny，Claude Code 负责人，2026 年 1 月发布于 X

这不是孤例。Andrej Karpathy 提到他从2025年下半年开始，几乎所有代码都是AI生成的，并持续公开记录自己在用 AI 完成越来越多的代码工作。我也亲眼所见 Yan Wang 鸭哥 过去一个季度，消耗超过 100 亿 tokens，产出几百万行代码，并且切实交付商业价值，基本全由 AI 生成。

这不是两个工具，这是同一个工具，在两种使用方式下的结果差距。

过去两年，我们的 AI 培训业务里，观察过几千名来自各个一线大厂的技术和管理人员。我们的结论是：说"AI 不靠谱"，几乎都是使用者能力层级的问题，不是工具本身的问题。

但到底差距在哪里？很多人总结为消耗token数量、能不能控制更多AI、能不能让AI跑更久，那些都是。真正有价值的是：差距到底在哪里？我们把它拆成五条，并且给出背后具体的技术能力。

## 差距 1：AI 的产出能不能直接用

普通员工给 AI 一个任务，来回改五六轮还不是自己想要的，最后干脆自己动手。AI Builder 的 AI 产出大多数时候可以直接用，偶尔需要微调，越用越准。

差距的根源不是 prompt 写得好不好。而在于 AI 在执行任务时能拿到什么信息。

**Document-First** 是核心原则：把项目规范、风格指南、验收标准写成结构化文档，让 AI 可以主动读取。AI 读不到的信息，在它的世界里就是不存在的。你的风格偏好、历史决策、设计约束——如果只存在于你的脑子里，AI 永远猜不准。

**Context Curation** 是第二层：管理 context window 的质量，不让无关信息稀释权重，不让关键信息缺席。很多人的 AI 失效，不是 prompt 写错了，而是 context 太脏。

**结果导向指令** 是第三层：告诉 AI 产出应该长什么样，而不是一步一步教它怎么做。规定格式、结构、边界条件，而不是过程。

## 差距 2：能不能系统性地判断质量、诊断问题

普通员工 AI 做完了凭感觉看一眼，觉得"好像对"就用了。出了问题不知道为什么，换个 prompt 重试碰运气。AI Builder 有明确的验收标准，能诊断根因，针对性地修。

这条差距决定了一个人的 AI 使用能不能持续进步，还是永远在同一水平来回试错。

**Evaluation Design** ：每个任务都应该有可执行的验收标准。不是"感觉好"，而是"满足 X 条件、不出现 Y 情况"。让 AI 在给出最终答案之前先对照标准自检，是一个简单但极有效的质量闸门。

**AI Debug 方法论** ：AI 失效有几种本质上不同的根因

- context 缺失导致的 hallucination、
- context window 饱和导致的信息丢失、
- 指令歧义导致的方向偏差、以及
- 模型能力边界本身的限制。

这四类问题的修法完全不同。不能诊断根因，只能盲猜。能有效debug，背后是对AI底层原理的直觉理解。

**观测性设计** ：要求 AI 暴露推理过程（rationale、中间步骤），而不是只看最终输出。黑盒输出无法调试；可见的推理链让问题暴露在早期。

*截图是我们* [*Builder Space*](https://www.superlinear.academy/c/ai-resources/ai-builder-space) *的debugger功能，把agent思考和工具调用的每一步展开，形成卡片，可观测、可修正。*

## 差距 3：能不能把完整任务 delegate 给 AI

普通员工一个指令一个指令地喂，每步都盯着，AI 干活的时候人在旁边空转。AI Builder 一段话 delegate 一个完整目标，AI 自己拆解、执行、检查，人去做别的事。

> *"I have never had this much joy day to day in my work, as I do right now, because essentially all the tedious work, Claude does it, and I get to be creative. I get to think about what I want to build next."*

— Boris Cherny，Fortune 专访，2026 年 1 月

这是产出倍增器的核心机制。AI自己迭代工作，把人解放出来，才是有效 leverage 自己的时间。这里所需的核心技能反而不是multi-agent，或者harness，而是更本质的一些技能：

**Agentic Loop** ：搭建 AI 自己迭代的闭环。不是"你做，我看，我改"，而是"AI 执行 → AI 自检 → AI 诊断 → AI 修改 → AI 再检查"。人只需要在循环收敛之后介入。这个闭环需要主动设计系统结构来触发，不会自己出现。

**Skill Writing** ：把复杂任务的执行方式编码成可复用的 skill 文档。AI 读了 skill 就知道如何拆解这类任务。这是从"教 AI 做这件事"到"给 AI 一个通用能力模块"的跨越。

**脚手架管理** ：知道什么时候加约束（任务不熟时给 AI 高密度指引），什么时候放手（AI 已经证明能做好时移除过度限制）。过度管控和过度放权都是浪费。

## 差距 4：AI 使用经验能不能积累复利

普通员工上个月踩过的坑这个月还会踩，每个人的 AI 技巧锁在自己的聊天记录里，新人来了从零开始。AI Builder 的经验在持续积累：一个人发现的盲区自动变成全组的检查规则，系统越用越强，新人 clone repo 半天上手。

个人的 AI 技巧是线性的；团队的 context 系统是复利的。区别在于你有没有把经验外化成系统。

**Context Architecture** ：设计团队级的 context 组织方式——什么信息放哪里、如何索引、如何更新、谁来维护。本质上是知识管理问题，只是载体是 AI 可以读取的结构化文档。

[**AGENTS.md**](http://agents.md/) **+** [**MEMORY.md**](http://memory.md/) ：定义 AI 的行为规范和知识沉淀机制。一个人踩过的坑、形成的判断原则，经过提炼后写进 [MEMORY.md](http://memory.md/) ，就自动变成全组 AI 的认知基础。这是经验从个人变成组织资产的通道： 为什么AI只会说正确的废话，以及怎么把它逼出舒适区 ； 你团队的 AI 效果不好，问题不在模型，在 Context

**Progressive Disclosure** ：按需加载 context，不一次性塞满 context window。重要的前置信息优先加载；细节在任务推进时逐步引入。这既是性能优化，也是让 AI 始终在高信噪比状态下工作的关键。

## 差距 5：AI 是执行工具，还是思考伙伴

普通员工用 AI 加速已有的工作流：写代码更快、做配表更准、生图更多。AI 的角色是执行工具，你告诉它做什么它就做什么。AI Builder 的 AI 会出现在意想不到的地方：帮你在一个你不擅长的领域做出有判断力的工作，发现你的决策和你自己定的原则之间的矛盾，提出一个你在自己的认知框架内不会想到的方向。

这条差距是前四条做到之后的自然涌现，没有办法直接"学会"。

当 AI 积累了足够密度的 context——你的价值判断、历史决策、工作原则、认知边界——它开始有能力做一件事：在你的盲区给出有质量的判断。这不是魔法，是信息密度达到阈值之后的结果。

**Context 密度是触发条件** ：axiom、memory、历史决策记录积累到足够量级之后，AI 有了做独立判断的信息基础。 **分层提炼是关键** ：不是把所有文档扔给 AI，而是从原始工作记录里蒸馏出稳定的判断原则——噪音去掉，信号留下。

达到这个状态的人，不会再讨论"AI 靠不靠谱"。他们在问的问题是：这个 AI 对我的理解深不深、它的判断边界在哪里、我还需要为它补充哪些 context。

> *"Not all of the things people learned in the past translate to coding with LLMs. The model can fill in the details."*

— Boris Cherny，2026 年 1 月

Context 密度分层提炼前四条的自然延伸

这五条差距之间不是并列关系。前两条是基础：能产出可用结果、能判断质量。第三条是杠杆：一个人驱动多个 agent 并行工作。第四条是飞轮：经验转化为系统，系统越跑越强。第五条是终点：AI 从工具变成真正意义上的协作者。

每一条都有对应的技术实践。每一条差距的背后都不是天赋，而是方法。

当然，这些方法在我们课程里都有教。如果感兴趣的话，最新一期直播课程正要开始，欢迎报名： 旗舰 AI 课程 《Build with AI》 第十二期报名截止，还剩 4 天

谢谢分享，很受益！