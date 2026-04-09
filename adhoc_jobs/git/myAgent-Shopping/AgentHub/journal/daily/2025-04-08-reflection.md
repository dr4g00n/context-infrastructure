# 次日行动清单 - Agora Agent Platform 端到端测试

> 日期: 2025-04-09
> 目标: 完成端到端测试，验证 Hub-Agent 消息流转

---

## 一、测试前准备

### 1.1 环境检查清单

- [ ] Docker 已安装并运行
- [ ] Python 3.11+ 环境可用
- [ ] 项目依赖已安装: `pip install -e ".[dev]"`
- [ ] 端口 1883 (MQTT) 和 8083 (WebSocket) 未被占用

### 1.2 确认文件完整性

```bash
# 检查关键文件是否存在
ls -la /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/hub/main.py
ls -la /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agents/echo_agent/agent.py
ls -la /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agents/calculator_agent/agent.py
ls -la /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/docker-compose.yml
```

---

## 二、启动 Hub（步骤 1）

### 2.1 启动命令

```bash
cd /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform
docker-compose up hub
```

### 2.2 代码指针

| 项目 | 路径 |
|------|------|
| Hub 主程序 | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/hub/main.py` |
| Hub 配置文件 | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/hub/config.yaml` |
| Docker 配置 | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/docker-compose.yml` |
| Dockerfile | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/hub/Dockerfile` |
| 认证令牌 | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/tokens.json` |

### 2.3 Hub 配置详情

```yaml
# hub/config.yaml
mqtt:
  host: "0.0.0.0"
  port: 1883
  ws_port: 8083
auth:
  type: token
  tokens_file: ./tokens.json
heartbeat:
  interval_seconds: 30
  timeout_seconds: 60
```

### 2.4 成功标志

Hub 启动成功时，控制台应输出：
```
Starting Agora Hub on 0.0.0.0:1883
Hub ready. Waiting for messages...
```

---

## 三、启动 Agent（步骤 2）

### 3.1 启动 Echo Agent

**终端 1**（Hub 保持运行）：
```bash
cd /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform
python -m agents.echo_agent.agent
```

### 3.2 启动 Calculator Agent（可选，用于多 Agent 测试）

**终端 2**：
```bash
cd /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform
python -m agents.calculator_agent.agent
```

### 3.3 代码指针

| 项目 | 路径 |
|------|------|
| Echo Agent | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agents/echo_agent/agent.py` |
| Echo Manifest | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agents/echo_agent/manifest.yaml` |
| Calculator Agent | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agents/calculator_agent/agent.py` |
| Calculator Manifest | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agents/calculator_agent/manifest.yaml` |
| Agent 基类 | `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agora/agent/base.py` |

### 3.4 Agent 认证令牌

```json
// tokens.json
{
  "echo_agent": "echo_key_123",
  "calculator_agent": "calc_key_123"
}
```

### 3.5 成功标志

Agent 启动成功时：
- Hub 控制台显示: `Agent registered: echo_agent`
- Agent 控制台显示连接成功信息

---

## 四、测试消息发送（步骤 3）

### 4.1 测试 1: 基础发现测试

```bash
cd /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform
python examples/basic_discovery.py
```

**预期输出**：
```
Discovering math agents...
Found 1 agents:
  - calculator_agent
```

### 4.2 测试 2: 多 Agent 消息发送

```bash
cd /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform
python examples/multi_agent_chat.py
```

**预期输出**：
```
Message sent to echo agent
```

### 4.3 测试 3: 直接发送消息到 Echo Agent

创建测试脚本 `/Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/test_send.py`：

```python
#!/usr/bin/env python3
import asyncio
import uuid
from agora.protocol.transport import MqttTransport
from agora.protocol.message import Message

async def main():
    transport = MqttTransport("localhost", 1883)
    await transport.connect()

    msg = Message(
        msg_id=str(uuid.uuid4()),
        from_agent="test_client",
        to_agent="echo_agent",
        capability="echo.send",
        payload={"message": "Hello Agora!"}
    )

    await transport.publish("agora/agent/echo_agent/inbox", msg)
    print(f"[SENT] Message to echo_agent: {msg.payload}")

    # 等待响应
    await asyncio.sleep(2)
    await transport.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

运行：
```bash
python test_send.py
```

---

## 五、验证检查点

### 5.1 Hub 端验证

Hub 控制台应显示以下日志：

```
# Agent 注册时
Agent registered: echo_agent

# 收到心跳时
Heartbeat from: echo_agent

# 收到发现请求时（调用 basic_discovery.py）
# （无显式日志，但会返回响应）

# 收到消息时
# （消息会转发到目标 Agent）
```

### 5.2 Agent 端验证

Echo Agent 控制台应显示：
```
Received: {'message': 'Hello Agora!'}
```

### 5.3 完整流程验证清单

- [ ] Hub 成功启动，监听 1883 端口
- [ ] Echo Agent 成功注册到 Hub
- [ ] Calculator Agent 成功注册到 Hub（如启动）
- [ ] basic_discovery.py 能发现 calculator_agent
- [ ] multi_agent_chat.py 成功发送消息
- [ ] Echo Agent 收到并处理消息
- [ ] 心跳消息正常（每 30 秒一次）

---

## 六、可能遇到的问题及解决方案

### 6.1 MQTT 连接问题

**现象**：`Connection refused` 或 `Connection timeout`

**排查步骤**：
```bash
# 1. 检查端口占用
lsof -i :1883

# 2. 检查 Docker 容器状态
docker-compose ps

# 3. 查看 Hub 日志
docker-compose logs hub
```

**解决方案**：
- 确保 Hub 完全启动后再启动 Agent（Hub 启动需要 5-10 秒）
- 检查防火墙设置，确保 1883 端口可访问
- 重启 Hub: `docker-compose down && docker-compose up hub`

### 6.2 端口冲突

**现象**：`Address already in use`

**解决方案**：
```bash
# 查找占用进程
lsof -i :1883

# 终止占用进程
kill -9 <PID>

# 或修改 docker-compose.yml 使用其他端口
# ports:
#   - "1884:1883"  # 使用 1884 代替 1883
```

### 6.3 认证失败

**现象**：`Authentication failed` 或 `Agent registration rejected`

**排查**：
```bash
# 检查 tokens.json 内容
cat /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/tokens.json

# 检查 Agent manifest 中的 api_key
cat /Users/dr4/WorkSpace/context-infrastructure/.worktrees/agora-agent-platform/agents/echo_agent/manifest.yaml
```

**解决方案**：
- 确保 `tokens.json` 中的 key 与 Agent manifest 中的 `api_key` 匹配
- 默认令牌：
  - echo_agent: `echo_key_123`
  - calculator_agent: `calc_key_123`

### 6.4 消息未送达

**现象**：发送消息但 Agent 未收到

**排查步骤**：
1. 确认 Agent 已注册: 检查 Hub 日志是否有 `Agent registered`
2. 确认 topic 正确: 应为 `agora/agent/{agent_id}/inbox`
3. 检查消息格式: 使用 `Message` 类序列化

### 6.5 Docker 构建失败

**现象**：`docker-compose up` 失败

**解决方案**：
```bash
# 清理并重建
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up hub
```

---

## 七、测试完成后的操作

### 7.1 停止服务

```bash
# 停止 Hub（在 Hub 终端按 Ctrl+C 后）
docker-compose down

# 停止 Agents（在各 Agent 终端按 Ctrl+C）
```

### 7.2 清理日志

```bash
# 清理 Docker 日志
docker system prune -f
```

---

## 八、成功标准总结

| 测试项 | 成功标志 |
|--------|----------|
| Hub 启动 | 控制台输出 `Hub ready. Waiting for messages...` |
| Agent 注册 | Hub 显示 `Agent registered: {agent_id}` |
| 心跳正常 | Hub 定期显示 `Heartbeat from: {agent_id}` |
| 服务发现 | `basic_discovery.py` 返回 Agent 列表 |
| 消息发送 | `multi_agent_chat.py` 执行无错误 |
| 消息接收 | Echo Agent 显示 `Received: {...}` |

---

## 九、明日优先级

1. **P0**: 启动 Hub 并验证运行状态
2. **P0**: 启动 Echo Agent 并完成注册
3. **P0**: 运行 multi_agent_chat.py 完成端到端消息测试
4. **P1**: 启动 Calculator Agent 并测试服务发现
5. **P1**: 运行 basic_discovery.py 验证发现机制
6. **P2**: 检查心跳和超时机制是否正常工作

---

*生成时间: 2025-04-08*
*项目: Agora Agent Platform*
