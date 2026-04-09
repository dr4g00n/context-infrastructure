# Agora Agent Platform 设计文档

**日期**: 2025-04-08  
**版本**: v1.0  
**状态**: 待评审

---

## 1. 项目概述

Agora 是一个面向 Agent 网络的注册、能力声明和互相发现平台。采用中心协调模式，所有 Agent 通过 MQTT 连接到中心 Hub，实现异步消息通信。

### 核心目标
- Agent 自动注册与发现
- 结构化能力声明与匹配
- 异步消息路由与负载均衡
- 水平扩展的基础架构

---

## 2. 架构设计

### 2.1 部署拓扑

采用 **中心协调模式（Hub-Spoke）**：

```
┌─────────────────────────────────────┐
│              Hub (MQTT Broker)       │
│  ┌──────────┐ ┌──────────┐          │
│  │ Registry │ │  Router  │          │
│  │  (内存)   │ │ (最少连接)│          │
│  └──────────┘ └──────────┘          │
└────────┬────────────────────┬────────┘
         │ MQTT               │ MQTT
    ┌────┴────┐          ┌────┴────┐
    │ Agent A │          │ Agent B │
    │Calculator│         │  LLM    │
    └─────────┘          └─────────┘
```

### 2.2 核心组件

#### Hub (中心节点)
- **MQTT Broker**: 基于 `aiomqtt` 或 `paho-mqtt` 实现
- **Registry**: 内存中的 Agent 注册表，存储 Agent ID、连接信息、能力列表、负载状态
- **Router**: 基于"最少连接"策略的消息路由决策器
- **Queue Manager**: 按目标 Agent ID 分队列管理消息，支持 TTL 过期清理

#### Agora Core (客户端库)
- `discovery/registry.py`: Agent 注册、注销、心跳管理
- `discovery/resolver.py`: 能力查询与 Agent 发现
- `protocol/message.py`: 消息结构定义与验证
- `protocol/transport.py`: MQTT 传输层封装
- `agent/base.py`: Agent 基类，提供消息收发框架

#### Agent (应用层)
- 继承 `AgentBase` 实现业务逻辑
- 通过 `manifest.yaml` 声明能力

---

## 3. 通信协议

### 3.1 传输层

- **协议**: MQTT 3.1.1
- **端口**: 1883 (TCP), 8083 (WebSocket 备用)
- **QoS**: 1 (至少一次送达)
- **KeepAlive**: 60 秒

### 3.2 MQTT Topic 设计

| Topic | 方向 | 用途 |
|-------|------|------|
| `agora/hub/registry` | Agent → Hub | 注册/注销 |
| `agora/hub/heartbeat` | Agent → Hub | 心跳保活 |
| `agora/hub/discover` | Agent → Hub | 能力查询请求 |
| `agora/hub/events` | Hub → Agent | 事件广播（Agent 上下线） |
| `agora/agent/{id}/inbox` | Hub → Agent | 投递消息 |
| `agora/agent/{id}/rpc` | Agent ↔ Hub | 同步调用（未来扩展） |

### 3.3 消息格式

```json
{
  "msg_id": "550e8400-e29b-41d4-a716-446655440000",
  "from": "agent_a",
  "to": "agent_b",
  "capability": "math.add",
  "payload": {"a": 1, "b": 2},
  "timestamp": "2025-04-08T10:00:00Z",
  "ttl": 300,
  "correlation_id": null
}
```

字段说明：
- `msg_id`: 消息唯一标识（UUID）
- `from`: 发送方 Agent ID
- `to`: 目标 Agent ID（可为空，表示广播）
- `capability`: 目标能力标识符
- `payload`: 业务负载（JSON 对象）
- `timestamp`: ISO8601 格式时间戳
- `ttl`: 消息存活时间（秒）
- `correlation_id`: 用于请求-响应关联（可选）

---

## 4. 能力声明规范

### 4.1 manifest.yaml 结构

```yaml
agent:
  id: calculator_agent           # 全局唯一标识
  version: "1.0.0"              # 语义化版本
  description: "数学计算 Agent"   # 描述
  api_key: ${AGENT_API_KEY}     # 从环境变量读取

capabilities:
  - name: math.add               # 能力标识符（点分命名空间）
    description: "Add two numbers"
    input_schema:                # JSON Schema 输入验证
      type: object
      required: ["a", "b"]
      properties:
        a: {type: number}
        b: {type: number}
    output_schema:               # JSON Schema 输出验证
      type: object
      properties:
        result: {type: number}
    
  - name: math.multiply
    description: "Multiply two numbers"
    input_schema:
      type: object
      required: ["a", "b"]
      properties:
        a: {type: number}
        b: {type: number}
    output_schema:
      type: object
      properties:
        result: {type: number}
```

### 4.2 能力匹配规则

- **精确匹配**: `math.add` 匹配 `math.add`
- **命名空间匹配**: `math.*` 匹配所有 math 命名空间下的能力
- **通配符查询**: `*` 匹配所有能力

---

## 5. 核心流程

### 5.1 Agent 注册流程

```
1. Agent 启动
   ↓
2. 读取 manifest.yaml，加载能力声明
   ↓
3. 连接 MQTT Broker (agora/hub)
   ↓
4. 订阅 agora/agent/{agent_id}/inbox
   ↓
5. 发送注册消息到 agora/hub/registry
   {
     "type": "register",
     "agent_id": "calculator_agent",
     "api_key": "xxx",
     "capabilities": [...],
     "endpoint": "mqtt://hub:1883"
   }
   ↓
6. Hub 验证 API Key，写入 Registry
   ↓
7. Hub 广播 agent_online 事件到 agora/hub/events
   ↓
8. Agent 启动成功，进入消息处理循环
```

### 5.2 消息发送流程

```
1. Agent A 调用 send_to_capability("math.add", payload)
   ↓
2. Agora Core 构造消息，msg_id 自动生成
   ↓
3. 消息发送到 agora/hub/discover（内部 topic）
   ↓
4. Hub Router 查询 Registry：
    - 筛选具有 math.add 能力的在线 Agent
    - 按当前负载排序（最少连接优先）
   ↓
5. 选择 Agent B 作为目标
   ↓
6. 消息入队 agent_b_inbox，TTL = 300 秒
   ↓
7. Hub 通过 MQTT 推送消息到 Agent B
   ↓
8. Agent B 收到消息，调用 handle_message()
   ↓
9. Agent B 发送响应（如需要）到 Agent A inbox
```

### 5.3 心跳与故障检测

- **心跳间隔**: 30 秒
- **超时阈值**: 60 秒（2 个心跳周期）
- **检测方式**: Hub 记录最后心跳时间，定时扫描超时 Agent
- **清理动作**: 
  - 标记 Agent 为离线
  - 清理该 Agent 的消息队列
  - 广播 agent_offline 事件

---

## 6. Hub 配置规范

```yaml
# hub/config.yaml
hub:
  # MQTT 配置
  mqtt:
    port: 1883
    ws_port: 8083
    max_connections: 10000
    
  # 认证配置
  auth:
    type: token
    tokens_file: ./tokens.json
    # tokens.json 格式: {"agent_id": "api_key"}
    
  # 消息队列配置
  queue:
    ttl_seconds: 300           # 消息存活时间
    max_size_per_agent: 1000   # 每个 Agent 队列上限
    cleanup_interval: 60       # 清理周期（秒）
    
  # 心跳配置
  heartbeat:
    interval_seconds: 30
    timeout_seconds: 60
    check_interval: 10
    
  # 日志配置
  logging:
    level: INFO
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## 7. API 接口（Python SDK）

### 7.1 AgentBase 类

```python
from agora.agent.base import AgentBase

class CalculatorAgent(AgentBase):
    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.capability == "math.add":
            result = message.payload["a"] + message.payload["b"]
            return Message(
                to=message.from,
                capability="math.add.response",
                payload={"result": result}
            )
        return None

# 启动 Agent
agent = CalculatorAgent(
    manifest_path="manifest.yaml",
    hub_host="localhost",
    hub_port=1883
)
await agent.start()
```

### 7.2 核心方法

| 方法 | 说明 |
|------|------|
| `start()` | 启动 Agent，完成注册和消息循环 |
| `stop()` | 优雅停止，发送注销消息 |
| `send_to_capability(capability, payload)` | 向指定能力发送消息 |
| `send_to_agent(agent_id, payload)` | 向指定 Agent 发送消息 |
| `discover_capabilities(pattern)` | 发现匹配的能力列表 |
| `discover_agents(capability)` | 发现具有指定能力的 Agent |

---

## 8. 内置 Agent

### 8.1 echo_agent

测试用 Agent，原样返回收到的消息。

### 8.2 calculator_agent

基础数学计算能力：
- `math.add`: 加法
- `math.subtract`: 减法
- `math.multiply`: 乘法
- `math.divide`: 除法

### 8.3 llm_agent

对接 LLM API，提供自然语言处理能力：
- `llm.chat`: 对话
- `llm.summarize`: 文本摘要
- `llm.translate`: 翻译

---

## 9. 测试策略

### 9.1 单元测试

- Agent 基类测试
- 消息编解码测试
- 能力匹配算法测试
- 负载均衡策略测试

### 9.2 集成测试

- Agent 注册/注销流程
- 消息收发端到端测试
- 心跳超时检测测试
- 多 Agent 并发场景

### 9.3 示例验证

- `basic_discovery.py`: 验证 Agent 发现功能
- `multi_agent_chat.py`: 验证多 Agent 协作
- `distributed_task.py`: 验证任务分发

---

## 10. 部署方案

### 10.1 本地开发

```bash
# 启动 Hub
docker-compose up hub

# 运行 Agent
python -m agents.calculator_agent
```

### 10.2 Docker Compose

```yaml
version: '3.8'
services:
  hub:
    build: ./hub
    ports:
      - "1883:1883"
      - "8083:8083"
    volumes:
      - ./hub/config.yaml:/app/config.yaml
      - ./tokens.json:/app/tokens.json
```

---

## 11. 扩展规划

### 11.1 后续版本功能

| 功能 | 版本 | 说明 |
|------|------|------|
| 消息持久化 | v1.1 | 集成 Redis/RabbitMQ 支持离线消息持久化 |
| 同步调用 | v1.1 | request-response 模式，支持超时控制 |
| 发布订阅 | v1.2 | Topic 订阅模式，支持广播 |
| WebSocket 网关 | v1.2 | 浏览器/移动端接入 |
| 分布式 Hub | v2.0 | 多 Hub 集群，状态共享 |
| gRPC 传输 | v2.0 | 高性能二进制通信 |
| 动态凭证 | v2.0 | JWT 令牌，自动刷新 |

### 11.2 边界情况

- **Agent 名称冲突**: Hub 拒绝同名注册，返回错误
- **队列溢出**: 超限时新消息丢弃，记录警告日志
- **无效能力**: 匹配失败时返回明确错误
- **循环调用**: 通过 correlation_id 追踪，设置最大跳转次数

---

## 12. 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Hub 单点故障 | 高 | 后续版本支持集群模式；当前支持状态快照恢复 |
| 消息丢失 | 中 | 内存队列 + TTL，重要消息建议应用层重试 |
| 认证泄露 | 高 | API Key 从环境变量读取，不在代码中硬编码 |
| 并发瓶颈 | 中 | 支持 10k 连接；超限需水平扩展 |

---

## 13. 附录

### 13.1 术语表

- **Agent**: 具有特定能力的自治实体
- **Capability**: Agent 声明的可执行能力
- **Hub**: 中心协调节点，负责注册和路由
- **Registry**: Agent 注册表
- **TTL**: Time To Live，消息存活时间

### 13.2 参考文档

- [MQTT 3.1.1 协议规范](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
- [JSON Schema](https://json-schema.org/)

---

## 评审记录

| 日期 | 评审人 | 意见 | 状态 |
|------|--------|------|------|
| | | | |
