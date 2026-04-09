# A2A Protocol Debugger 开发计划

> **计划用途**: 本计划仅用于设计阶段参考，不做编码执行

## 目标

构建一套完整的 A2A (Agent-to-Agent) 协议调试工具，支持：
- 消息拦截与记录
- 可视化调试界面
- 协议合规检查
- 时序分析与故障诊断

---

## 项目结构

```
a2a_debugger/
├── pyproject.toml              # 项目配置
├── README.md                   # 使用说明
├── src/
│   └── a2a_debugger/
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── message.py      # A2AMessage 数据模型
│       ├── proxy/
│       │   ├── __init__.py
│       │   └── debug_proxy.py  # A2ADebugProxy 拦截代理
│       ├── analyzer/
│       │   ├── __init__.py
│       │   ├── validator.py    # 协议验证
│       │   └── conversation.py # 对话分析
│       └── web/
│           ├── __init__.py
│           └── dashboard.py    # Streamlit 调试界面
├── tests/
│   ├── __init__.py
│   ├── test_message.py
│   ├── test_proxy.py
│   ├── test_validator.py
│   └── test_analyzer.py
└── examples/
    ├── simple_agent.py         # 示例 Agent
    └── test_scenario.py        # 测试场景
```

---

## 开发阶段

### Phase 1: 核心数据模型 (Day 1)

**1.1 A2AMessage 数据模型**

- 字段设计: id, timestamp, source, target, protocol_version, message_type, payload, headers, metadata
- 序列化/反序列化方法
- 消息分类: request/response/notification

**1.2 消息存储机制**

- 内存存储 (开发阶段)
- 持久化接口预留 (SQLite/文件)
- 消息日志检索接口

---

### Phase 2: 调试代理 (Day 1-2)

**2.1 A2ADebugProxy 核心**

- 基于 aiohttp 的代理服务器
- 请求拦截与记录
- 响应拦截与记录
- 请求-响应关联

**2.2 Hook 系统**

- 异步钩子注册
- 消息处理管道
- 实时告警钩子示例

**2.3 代理配置**

- 目标主机配置
- 监听端口配置
- SSL/TLS 支持预留

---

### Phase 3: 协议验证 (Day 2)

**3.1 基础验证器**

- JSON-RPC 版本检查
- 必需字段检查 (method, id, jsonrpc)
- 消息 ID 格式验证

**3.2 高级验证**

- A2A 协议特定字段检查
- 自定义验证规则支持
- 验证结果报告

---

### Phase 4: 可视化界面 (Day 3)

**4.1 Streamlit 仪表盘**

- 实时消息流展示
- 消息详情查看
- 基础统计 (消息数、错误率)

**4.2 高级可视化**

- 通信拓扑图 (networkx + matplotlib)
- 时序图
- 延迟分析图表

**4.3 交互功能**

- 消息过滤
- 时间范围选择
- 导出功能

---

### Phase 5: 对话分析 (Day 3-4)

**5.1 ConversationAnalyzer**

- 构建通信图
- 循环依赖检测
- 消息时序分析

**5.2 延迟分析**

- 请求-响应延迟计算
- 按 Agent 统计延迟
- 异常延迟检测

**5.3 故障诊断**

- 超时检测
- 错误模式识别
- 诊断报告生成

---

### Phase 6: 测试与文档 (Day 4-5)

**6.1 单元测试**

- 数据模型测试
- 代理功能测试
- 验证器测试
- 分析器测试

**6.2 集成测试**

- 端到端调试场景
- 多 Agent 通信测试

**6.3 文档**

- 使用指南
- API 文档
- 示例代码

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 代理服务 | aiohttp |
| 可视化 | streamlit, plotly |
| 图分析 | networkx, matplotlib |
| 数据 | pydantic, dataclasses |
| 测试 | pytest, pytest-asyncio |

---

## 依赖清单

```toml
[project]
dependencies = [
    "aiohttp>=3.9.0",
    "streamlit>=1.28.0",
    "pandas>=2.0.0",
    "networkx>=3.2.0",
    "matplotlib>=3.8.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

---

## 关键设计决策

### 1. 消息存储
- **初期**: 内存列表 + 长度限制 (防止内存溢出)
- **后期**: 可选 SQLite 持久化

### 2. 代理架构
- 透明代理设计，不修改原始消息
- 异步处理支持高并发
- 钩子系统支持扩展

### 3. 验证策略
- 可配置的验证规则
- 支持自定义验证器
- 验证结果不影响消息转发

### 4. 可视化性能
- 消息流限制显示数量 (默认最新 100 条)
- 自动刷新间隔可配置
- 支持暂停刷新

---

## 使用示例 (规划)

```python
# 启动调试代理
proxy = A2ADebugProxy(
    target_host="http://localhost:8000",
    listen_port=8080
)
await proxy.start()

# 添加自定义钩子
async def alert_hook(msg: A2AMessage):
    if msg.metadata.get("status", 200) >= 500:
        print(f"Alert: Server error {msg.metadata['status']}")

proxy.add_hook(alert_hook)

# 启动 Web UI
streamlit run src/a2a_debugger/web/dashboard.py

# 分析对话
analyzer = ConversationAnalyzer(proxy.message_log)
cycles = analyzer.detect_cycles()
latency = analyzer.latency_analysis()
```

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 消息量过大导致内存溢出 | 设置消息日志上限，支持持久化 |
| Streamlit 性能瓶颈 | 限制显示数据量，支持暂停刷新 |
| 代理引入额外延迟 | 异步处理，最小化处理逻辑 |
| 协议版本兼容性 | 可配置的验证规则 |

---

## 里程碑

- **M1 (Day 2)**: 代理可运行，能拦截记录消息
- **M2 (Day 3)**: Web UI 可查看消息流
- **M3 (Day 4)**: 协议验证和基础分析功能完成
- **M4 (Day 5)**: 完整测试覆盖，文档齐全
