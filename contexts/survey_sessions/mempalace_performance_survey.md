# MemPalace 性能表现与基准测试深度调研报告

## 执行摘要

MemPalace 是 2026 年 4 月发布的开源 AI 记忆系统，在 LongMemEval 基准测试中取得了 **96.6% R@5** 的成绩（Raw 模式，零 API 调用），这是目前公开的最高零依赖记忆系统得分。然而，项目在发布初期存在多项性能声明争议，维护团队已通过公开声明进行了修正。

---

## 1. LongMemEval 基准测试详解

### 1.1 测试成绩与数据来源

**主要成绩：**

| 模式 | R@5 | R@10 | NDCG@10 | API 调用 | 数据来源 |
|------|-----|------|---------|----------|----------|
| **Raw ( headline )** | **96.6%** | 98.2% | 0.889 | 零 | 官方基准测试 |
| AAAK | 84.2% | 92.0% | 0.720 | 零 | Issue #39 独立验证 |
| Rooms | 89.4% | 95.6% | 0.789 | 零 | Issue #39 独立验证 |
| Hybrid v3 + Haiku | 99.4% | 99.6% | 0.975 | ~500 次 | 官方基准测试 |
| Hybrid v4 + Haiku | **100%** | 100% | 0.976 | ~500 次 | 官方基准测试 |

**数据来源：**
- 官方结果：`benchmarks/BENCHMARKS.md` [^1]
- 独立复现：Issue #39 [^2]

### 1.2 测试方法与数据集

**数据集：** LongMemEval-S (cleaned version)
- 500 个问题
- 每个问题平均跨 53 个对话会话
- 6 种问题类型：知识更新、多会话、时间推理、单会话用户、单会话偏好、单会话助手

**测试配置：**
```python
# 嵌入模型
Embedding: all-MiniLM-L6-v2 (ChromaDB 默认)
Vector DB: ChromaDB
Distance: Cosine similarity
```

**Raw 模式实现细节：**
- 每个会话作为独立文档存储
- 无摘要、无提取、无压缩
-  verbatim 原文存储
- 查询时使用句子转换器嵌入

### 1.3 独立复现方法

**复现步骤（来自 benchmarks/README.md）：**

```bash
# 1. 克隆仓库
git clone -b ben/benchmarking https://github.com/aya-thekeeper/mempal.git
cd mempal
pip install chromadb pyyaml

# 2. 下载数据
mkdir -p /tmp/longmemeval-data
curl -fsSL -o /tmp/longmemeval-data/longmemeval_s_cleaned.json \
  https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json

# 3. 运行 Raw 模式（96.6%）
python benchmarks/longmemeval_bench.py \
  /tmp/longmemeval-data/longmemeval_s_cleaned.json

# 4. 运行 AAAK 模式（84.2%）
python benchmarks/longmemeval_bench.py \
  /tmp/longmemeval-data/longmemeval_s_cleaned.json --mode aaak

# 5. 运行 Rooms 模式（89.4%）
python benchmarks/longmemeval_bench.py \
  /tmp/longmemeval-data/longmemeval_s_cleaned.json --mode rooms
```

**独立复现验证：**
- 用户 @gizmax 在 M2 Ultra (64GB) 上复现 [^2]
- 结果：Raw 96.6% 完全匹配
- 运行时间：4 分 37 秒
- 零修改、零依赖

---

## 2. 与其他系统的对比

### 2.1 LongMemEval R@5 排行榜

| 排名 | 系统 | R@5 | 需要 API | 成本 | 备注 |
|------|------|-----|----------|------|------|
| 1 | **MemPalace (hybrid v4 + rerank)** | **100%** | 可选 | 免费 | 首个满分 |
| 2 | Supermemory ASMR (实验版) | ~99% | 是 | - | 研究阶段 |
| 3 | **MemPalace (hybrid v3 + rerank)** | **99.4%** | 可选 | 免费 | 可复现 |
| 4 | **MemPalace (raw)** | **96.6%** | **否** | **免费** | **最高零 API 分** |
| 5 | Mastra | 94.87% | 是 (GPT) | API 成本 | [^3] |
| 6 | Hindsight | 91.4% | 是 (Gemini) | API 成本 | 弗吉尼亚理工验证 |
| 7 | Supermemory (生产版) | ~85% | 是 | - | |
| 8 | Mem0 | ~85% | 是 | $19-249/月 | [^4] |
| 9 | Zep | ~85% | 是 | $25/月+ | [^5] |
| 10 | Stella (dense) | ~85% | 否 | 免费 | 学术基线 |

**数据来源：** `benchmarks/BENCHMARKS.md` [^1]

### 2.2 ConvoMem 基准对比 (Salesforce, 75K+ QA)

| 系统 | 平均分 | 助手事实 | 用户事实 |
|------|--------|----------|----------|
| **MemPalace** | **92.9%** | 100% | 98.0% |
| Gemini (长上下文) | 70-82% | - | - |
| 块提取 | 57-71% | - | - |
| Mem0 (RAG) | 30-45% | - | - |

**关键发现：** MemPalace 在 ConvoMem 上是 Mem0 的 **2 倍以上**。

### 2.3 LoCoMo 基准对比 (1,986 QA pairs)

| 模式 | R@10 | 单跳 | 时间推理 | 时间推断 | 对抗性 |
|------|------|------|----------|----------|--------|
| Hybrid + Sonnet rerank | **100%** | 100% | 100% | **100%** | 100% |
| Hybrid v5 (无 rerank) | 88.9% | 72.1% | 90.8% | 70.0% | 95.3% |
| 基线 (session) | 60.3% | - | - | - | - |

---

## 3. 不同模式的性能差异分析

### 3.1 Raw 模式：96.6%（零 API 调用）

**工作原理：**
- 存储每个会话的 verbatim 原文
- 使用 ChromaDB 默认的 all-MiniLM-L6-v2 嵌入
- 纯语义搜索，无后处理

**为什么成绩好：**
- 不丢失信息：LLM 提取式记忆会丢弃上下文
- 完整的对话原文保留所有细节
- 嵌入模型能捕捉语义相似性

**官方定位：** "The field is over-engineering the memory extraction step. Raw verbatim text with good embeddings is a stronger baseline than anyone realized." [^1]

### 3.2 AAAK 模式：84.2%（-12.4 点）

**AAAK 是什么：**
- 缩写方言（lossy abbreviation dialect）
- 实体编码 + 结构标记 + 句子截断
- 设计目标：大规模重复实体的 token 压缩

**性能回归原因：**
1. **有损压缩**：信息在缩写过程中丢失
2. **小规模 overhead**：AAAK 在小文本上的编码开销反而增加 token
3. **设计场景不符**：AAAK 为大规模重复实体优化，LongMemEval 不适合

**重要澄清（来自官方声明）：** [^6]
- "AAAK is lossy, not lossless"
- "It does not save tokens at small scales"
- "AAAK currently regresses LongMemEval vs raw verbatim retrieval (84.2% R@5 vs 96.6%)"
- "The 96.6% headline number is from RAW mode, not AAAK mode"

### 3.3 Hybrid 模式演进

| 版本 | R@5 | 改进内容 | LLM 需求 |
|------|-----|----------|----------|
| Raw | 96.6% | 基线 | 否 |
| Hybrid v1 | 97.8% | +关键词重叠评分 | 否 |
| Hybrid v2 | 98.4% | +时间邻近性 boost | 否 |
| Hybrid v2 + rerank | 98.8% | +Haiku 重排序 | 是 |
| Hybrid v3 + rerank | 99.4% | +偏好提取（16 个模式） | 是 |
| **Hybrid v4 + rerank** | **100%** | +引号短语提取 +人名 boost +怀旧模式 | 是 |

**Hybrid v4 的三项关键修复：** [^1]
1. **引号短语提取**：问题中的 `'sexual compulsions'` 直接匹配
2. **人名 boost**：Rachel/ukulele 问题中的 "Rachel" 获得 40% 距离缩减
3. **怀旧模式**："I still remember" 等模式提取

### 3.4 Rooms 模式：89.4%

**Palace 结构：**
```
Wing (人/项目)
  └── Hall (记忆类型)
        └── Room (主题)
              └── Closet (摘要)
                    └── Drawer (原文)
```

**测试结果：**
- 独立架构验证：Palace + Haiku rerank 也达到 99.4%
- 证明性能上限是架构性的，非单一方法的局部最优

---

## 4. Palace 结构对检索的提升：+34% R@10

### 4.1 声明与数据

**原始声明：**
```
Search all closets:          60.9%  R@10
Search within wing:          73.1%  (+12%)
Search wing + hall:          84.8%  (+24%)
Search wing + room:          94.8%  (+34%)
```

### 4.2 争议与修正

**官方声明（2026-04-07）承认：** [^6]

> "'+34% palace boost' was misleading. That number compares unfiltered search to wing+room metadata filtering. Metadata filtering is a standard ChromaDB feature, not a novel retrieval mechanism. Real and useful, but not a moat."

**实际情况：**
- +34% 来自标准 ChromaDB 的元数据过滤
- 这是通用功能，非 MemPalace 独创
- 数据基于 22,000+ 真实对话记忆测试

### 4.3 独立验证发现

@gizmax 在 Issue #39 中指出：

> "the headline 96.6% is effectively a benchmark of `all-MiniLM-L6-v2` embeddings on this dataset rather than of the palace architecture itself"

**重要发现：**
- `--mode raw` 完全绕过 palace、wing、room 代码路径
- 96.6% 主要来自嵌入模型，非 palace 结构

---

## 5. 成本效益分析：$0.70/年 vs $507/年

### 5.1 对比数据

| 方案 | 加载 Token | 年成本 | 计算依据 |
|------|------------|--------|----------|
| 粘贴所有内容 | 19.5M | 不可能 | 超出任何上下文窗口 |
| LLM 摘要 | ~650K | **~$507/年** | 6 个月 AI 使用 |
| **MemPalace wake-up** | **~170 tokens** | **~$0.70/年** | L0 + L1 层 |
| MemPalace + 5 次搜索 | ~13,500 | ~$10/年 | 按需搜索 |

### 5.2 计算依据

**基础假设：** 6 个月日常 AI 使用 = 19.5M tokens [^7]

**MemPalace 分层架构：**
| 层级 | 内容 | Token 数 | 加载时机 |
|------|------|----------|----------|
| L0 | 身份（AI 是谁） | ~50 | 始终 |
| L1 | 关键事实（团队、项目、偏好） | ~120 (AAAK) | 始终 |
| L2 | 房间回忆（最近会话、当前项目） | 按需 | 话题触发 |
| L3 | 深度搜索（语义查询所有 closet） | 按需 | 显式请求 |

**实际验证差异：**
- README 声称：~170 tokens
- @gizmax 实测：`mempalace wake-up` 返回 ~810 tokens [^2]
- 官方回应：cli.py 帮助字符串说明 "~600-900 tokens"

### 5.3 成本计算争议

**批评点：**
- $507/年的对比基准未明确说明
- 未提供 LLM 摘要的具体实现和成本模型
- 实际 token 数与宣传存在差异

---

## 6. 基准测试的可复现性

### 6.1 benchmarks/ 目录结构

```
benchmarks/
├── README.md                    # 复现指南
├── BENCHMARKS.md                # 完整结果 + 方法论
├── HYBRID_MODE.md               # Hybrid 模式设计文档
├── longmemeval_bench.py         # LongMemEval 运行器
├── locomo_bench.py              # LoCoMo 运行器
├── convomem_bench.py            # ConvoMem 运行器
├── membench_bench.py            # MemBench 运行器
├── results_*.jsonl              # 原始结果文件
└── diary_cache_haiku.json       # 预计算日记主题
```

### 6.2 关键复现文件

**官方承诺：**
- 所有结果可审计：每道题、每个检索文档、每个分数
- 确定性：相同数据 + 相同脚本 = 相同结果
- 数据公开：LongMemEval、LoCoMo、ConvoMem 都是学术数据集

**已验证复现：**
- Issue #39: @gizmax 在 M2 Ultra 上复现 96.6%
- 时间：< 5 分钟
- 依赖：Python 3.9+、ChromaDB、零 API key

### 6.3 结果文件列表

| 文件 | 模式 | R@5 | 备注 |
|------|------|-----|------|
| `results_raw_full500.jsonl` | raw | 96.6% | 无 LLM |
| `results_aaak_full500.jsonl` | aaak | 84.2% | 压缩会话 |
| `results_rooms_full500.jsonl` | rooms | 89.4% | 会话房间 |
| `results_hybrid_v3_rerank_full500.jsonl` | hybrid+rerank | 99.4% | Haiku |
| `results_mempal_hybrid_v4_llmrerank_session_*.jsonl` | hybrid_v4+rerank | **100%** | Haiku/Sonnet |
| `results_lme_hybrid_v4_held_out_450_*.json` | hybrid_v4 held-out | 98.4% | 清洁分数 |

---

## 7. 性能声明的争议与修正

### 7.1 官方修正声明（2026-04-07）

Milla & Ben 发布公开声明 [^6]，承认以下问题：

**错误声明：**
1. **AAAK token 计数错误**
   - 声称：粗略启发式 `len(text)//3`
   - 实际：OpenAI tokenizer 显示英文 66 tokens → AAAK 73 tokens
   - 结论：AAAK 在小规模不节省 token

2. **"30x lossless compression" 夸大**
   - 声称：无损压缩
   - 实际：有损缩写系统
   - 回归：AAAK 84.2% vs Raw 96.6%（-12.4 点）

3. **"+34% palace boost" 误导**
   - 声称：Palace 结构提升
   - 实际：标准 ChromaDB 元数据过滤
   - 定性：有用但非护城河

4. **矛盾检测功能**
   - 声称：集成在知识图谱中
   - 实际：`fact_checker.py` 存在但未接入 KG

5. **"100% with Haiku rerank"**
   - 声称：公开可复现
   - 实际：结果存在但 rerank 管道未在公共脚本中

### 7.2 仍然成立和可复现的声明

✅ **96.6% R@5 on LongMemEval in raw mode**
- 500 题、零 API 调用
- 由 @gizmax 在 M2 Ultra 上 < 5 分钟独立复现

✅ **本地、免费、无订阅、无云、数据不出机器**

✅ **架构（wing、room、closet、drawer）真实且有用**
- 虽非神奇检索提升，但结构本身有价值

### 7.3 社区批评要点

**Issue #39 (@gizmax)：** [^2]
- 确认 Raw 96.6% 可复现
- 指出 AAAK/Rooms 相比 Raw 回归
- 发现 96.6% 主要来自嵌入模型而非 Palace 架构

**Issue #43 (@panuhorsmalahti)：** [^8]
- AAAK token 计数与实际 tokenizer 不符
- 被标记为 bug 并修复

**Issue #27 (@lhl)：**
- 性能声明质疑
- 官方在声明中致谢

### 7.4 方法论争议

**Hybrid v4 的 100% 结果：** [^1]

官方坦诚披露：
> "The hybrid v4 improvements (quoted phrase boost, person name boost, nostalgia patterns) were developed by directly examining the three specific questions that failed in every prior mode... This is teaching to the test."

**清洁分数：**
- 使用 50/450 训练/测试分割
- 450 题 held-out 分数：**98.4% R@5**（未调优）
- 这是官方推荐的"诚实可发布数字"

---

## 8. 关键结论

### 8.1 确认的优势

1. **零依赖高性能**：Raw 模式 96.6% 是真实的、可复现的、目前最高的零 API 记忆系统得分
2. **完整开源**：代码、数据、结果全部公开可审计
3. **架构诚实**：维护团队对批评的回应迅速且透明

### 8.2 需要注意的局限

1. **AAAK 非默认**：96.6% 来自 Raw 模式，非 AAAK
2. **Palace 结构非神奇**：+34% 来自标准元数据过滤
3. **成本对比未经验证**：$0.70 vs $507 的计算基础不透明
4. **100% 有争议**：Hybrid v4 针对特定失败案例调优，清洁分数 98.4%

### 8.3 与其他系统的选择建议

| 场景 | 推荐系统 | 理由 |
|------|----------|------|
| 零 API、本地优先 | **MemPalace Raw** | 96.6%、免费、开源 |
| 最高检索精度 | MemPalace Hybrid v4 + rerank | 100%（但有 API 成本） |
| 企业级、托管服务 | Zep / Mem0 | 成熟、支持好 |
| 生产环境稳定性 | Mastra | 94.87%、已验证 |

---

## 9. 参考链接

[^1]: [MemPalace benchmarks/BENCHMARKS.md](https://github.com/milla-jovovich/mempalace/blob/main/benchmarks/BENCHMARKS.md)
[^2]: [Issue #39 - Independent benchmark reproduction](https://github.com/milla-jovovich/mempalace/issues/39)
[^3]: [Mastra documentation](https://mastra.ai)
[^4]: [Mem0 pricing](https://mem0.ai/pricing)
[^5]: [Zep pricing](https://zep.ai/pricing)
[^6]: [README.md - A Note from Milla & Ben — April 7, 2026](https://github.com/milla-jovovich/mempalace/blob/main/README.md)
[^7]: [MemPalace main README](https://github.com/milla-jovovich/mempalace/blob/main/README.md)
[^8]: [Issue #43 - Incorrect token estimate for AAAK](https://github.com/milla-jovovich/mempalace/issues/43)

---

*报告生成时间：2026-04-09*  
*数据来源：GitHub 公开信息、官方文档、社区 issue*
