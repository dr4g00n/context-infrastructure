# Agora Agent Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a hub-based Agent registration, capability declaration, and discovery platform using MQTT as the transport layer.

**Architecture:** Center-coordinated Hub using MQTT broker for transport, in-memory registry for Agent management, TTL-based message queues, and "least-connections" routing strategy.

**Tech Stack:** Python 3.11+, asyncio, aiomqtt (MQTT client), paho-mqtt (MQTT broker integration), PyYAML, pytest, pytest-asyncio

---

## File Structure

```
agora/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # Basic usage documentation
├── docker-compose.yml          # Hub + example agents
│
├── agora/                      # Core library
│   ├── __init__.py
│   ├── protocol/
│   │   ├── __init__.py
│   │   ├── message.py          # Message dataclass and validation
│   │   ├── codec.py            # JSON encoding/decoding
│   │   └── transport.py        # MQTT transport abstraction
│   │
│   ├── discovery/
│   │   ├── __init__.py
│   │   ├── registry.py         # Agent registration client
│   │   ├── resolver.py         # Capability discovery
│   │   └── health.py           # Heartbeat management
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── base.py             # AgentBase class
│   │   ├── capability.py       # Capability declaration
│   │   └── context.py          # Agent context (state)
│   │
│   ├── routing/
│   │   ├── __init__.py
│   │   ├── router.py           # Message routing logic
│   │   └── load_balance.py     # Least-connections strategy
│   │
│   └── utils/
│       ├── __init__.py
│       ├── async_helper.py     # Async utilities
│       └── logging.py          # Structured logging
│
├── hub/                        # Central Hub service
│   ├── Dockerfile
│   ├── main.py                 # Hub entry point
│   ├── config.yaml             # Hub configuration
│   ├── registry.py             # In-memory Agent registry
│   ├── router.py               # Hub-side routing
│   ├── queue.py                # Message queue manager
│   ├── auth.py                 # Token-based authentication
│   ├── health_checker.py       # Heartbeat monitoring
│   └── web/                    # (Optional) Management UI
│       ├── index.html
│       └── dashboard.js
│
├── agents/                     # Built-in example agents
│   ├── __init__.py
│   ├── echo_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── manifest.yaml
│   ├── calculator_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── manifest.yaml
│   └── llm_agent/
│       ├── __init__.py
│       ├── agent.py
│       └── manifest.yaml
│
├── examples/
│   ├── basic_discovery.py
│   └── multi_agent_chat.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_message.py
│   │   ├── test_codec.py
│   │   ├── test_registry.py
│   │   └── test_load_balance.py
│   └── integration/
│       ├── test_agent_lifecycle.py
│       └── test_message_routing.py
│
└── docs/
    ├── architecture.md
    └── quickstart.md
```

---

## Implementation Tasks

### Task 1: Project Setup and Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `README.md` (basic)
- Create: `.gitignore`

- [ ] **Step 1.1: Create pyproject.toml**

Create with project metadata and dependencies:

```toml
[project]
name = "agora"
version = "0.1.0"
description = "Agent registration, capability declaration and discovery platform"
requires-python = ">=3.11"
dependencies = [
    "aiomqtt>=1.0.0",
    "paho-mqtt>=1.6.0",
    "pyyaml>=6.0",
    "structlog>=23.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

- [ ] **Step 1.2: Create basic README.md**

```markdown
# Agora

Agent registration, capability declaration and discovery platform.

## Quick Start

```bash
pip install -e ".[dev]"
```

## Run Hub

```bash
docker-compose up hub
```

## Run Example Agent

```bash
python -m agents.echo_agent
```
```

- [ ] **Step 1.3: Create .gitignore**

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.venv/
venv/
ENV/
.env
*.log
.DS_Store
```

- [ ] **Step 1.4: Install dependencies and verify**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -c "import agora; print('OK')"
```

Expected: OK (import fails because package doesn't exist yet, that's fine)

- [ ] **Step 1.5: Commit**

```bash
git add pyproject.toml README.md .gitignore
git commit -m "chore: initial project setup"
```

---

### Task 2: Message Protocol Layer

**Files:**
- Create: `agora/__init__.py`
- Create: `agora/protocol/__init__.py`
- Create: `agora/protocol/message.py`
- Create: `agora/protocol/codec.py`
- Test: `tests/unit/test_message.py`
- Test: `tests/unit/test_codec.py`

- [ ] **Step 2.1: Write failing test for Message dataclass**

Create `tests/unit/test_message.py`:

```python
import pytest
from datetime import datetime
from agora.protocol.message import Message


class TestMessage:
    def test_message_creation(self):
        msg = Message(
            msg_id="550e8400-e29b-41d4-a716-446655440000",
            from_agent="agent_a",
            to_agent="agent_b",
            capability="math.add",
            payload={"a": 1, "b": 2},
            timestamp=datetime(2025, 4, 8, 10, 0, 0),
            ttl=300
        )
        assert msg.msg_id == "550e8400-e29b-41d4-a716-446655440000"
        assert msg.from_agent == "agent_a"
        assert msg.to_agent == "agent_b"
        assert msg.capability == "math.add"
        assert msg.payload == {"a": 1, "b": 2}
        assert msg.ttl == 300
        assert msg.correlation_id is None

    def test_message_validation_missing_required(self):
        with pytest.raises(TypeError):
            Message(from_agent="agent_a")

    def test_message_default_ttl(self):
        msg = Message(
            msg_id="test-id",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )
        assert msg.ttl == 300
```

- [ ] **Step 2.2: Run test to verify it fails**

```bash
pytest tests/unit/test_message.py -v
```

Expected: ImportError or ModuleNotFoundError for agora.protocol.message

- [ ] **Step 2.3: Implement Message dataclass**

Create `agora/protocol/message.py`:

```python
"""Message format definitions for Agora protocol."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Message:
    """A message exchanged between Agents.
    
    Attributes:
        msg_id: Unique message identifier (UUID)
        from_agent: Sender Agent ID
        to_agent: Target Agent ID (empty for broadcast)
        capability: Target capability identifier
        payload: Business payload (JSON-serializable dict)
        timestamp: ISO8601 format timestamp
        ttl: Time-to-live in seconds (default: 300)
        correlation_id: For request-response correlation (optional)
    """
    msg_id: str
    from_agent: str
    to_agent: str
    capability: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ttl: int = 300
    correlation_id: str | None = None

    def is_expired(self) -> bool:
        """Check if message has exceeded its TTL."""
        from datetime import timedelta
        return datetime.utcnow() > self.timestamp + timedelta(seconds=self.ttl)
```

- [ ] **Step 2.4: Run tests to verify they pass**

```bash
pytest tests/unit/test_message.py -v
```

Expected: 3 tests PASSED

- [ ] **Step 2.5: Write failing test for JSON codec**

Create `tests/unit/test_codec.py`:

```python
import pytest
from datetime import datetime
from agora.protocol.message import Message
from agora.protocol.codec import MessageCodec


class TestMessageCodec:
    def test_encode_message(self):
        msg = Message(
            msg_id="550e8400-e29b-41d4-a716-446655440000",
            from_agent="agent_a",
            to_agent="agent_b",
            capability="math.add",
            payload={"a": 1, "b": 2},
            timestamp=datetime(2025, 4, 8, 10, 0, 0),
            ttl=300
        )
        encoded = MessageCodec.encode(msg)
        assert isinstance(encoded, bytes)
        assert b"550e8400" in encoded

    def test_decode_message(self):
        json_str = '''{
            "msg_id": "550e8400-e29b-41d4-a716-446655440000",
            "from": "agent_a",
            "to": "agent_b",
            "capability": "math.add",
            "payload": {"a": 1, "b": 2},
            "timestamp": "2025-04-08T10:00:00",
            "ttl": 300,
            "correlation_id": null
        }'''
        msg = MessageCodec.decode(json_str.encode())
        assert msg.msg_id == "550e8400-e29b-41d4-a716-446655440000"
        assert msg.from_agent == "agent_a"
        assert msg.capability == "math.add"
        assert msg.payload == {"a": 1, "b": 2}

    def test_roundtrip(self):
        original = Message(
            msg_id="test-id",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={"key": "value"}
        )
        encoded = MessageCodec.encode(original)
        decoded = MessageCodec.decode(encoded)
        assert decoded.msg_id == original.msg_id
        assert decoded.from_agent == original.from_agent
        assert decoded.payload == original.payload
```

- [ ] **Step 2.6: Run test to verify it fails**

```bash
pytest tests/unit/test_codec.py -v
```

Expected: ImportError for agora.protocol.codec

- [ ] **Step 2.7: Implement MessageCodec**

Create `agora/protocol/codec.py`:

```python
"""Message encoding and decoding."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from agora.protocol.message import Message


class MessageCodec:
    """JSON codec for Message objects."""

    @staticmethod
    def encode(msg: Message) -> bytes:
        """Encode Message to JSON bytes."""
        data = {
            "msg_id": msg.msg_id,
            "from": msg.from_agent,
            "to": msg.to_agent,
            "capability": msg.capability,
            "payload": msg.payload,
            "timestamp": msg.timestamp.isoformat(),
            "ttl": msg.ttl,
            "correlation_id": msg.correlation_id
        }
        return json.dumps(data, separators=(',', ':')).encode('utf-8')

    @staticmethod
    def decode(data: bytes) -> Message:
        """Decode JSON bytes to Message."""
        obj = json.loads(data.decode('utf-8'))
        return Message(
            msg_id=obj["msg_id"],
            from_agent=obj["from"],
            to_agent=obj["to"],
            capability=obj["capability"],
            payload=obj["payload"],
            timestamp=datetime.fromisoformat(obj["timestamp"]),
            ttl=obj["ttl"],
            correlation_id=obj.get("correlation_id")
        )
```

- [ ] **Step 2.8: Run tests to verify they pass**

```bash
pytest tests/unit/test_codec.py -v
```

Expected: 3 tests PASSED

- [ ] **Step 2.9: Commit**

```bash
git add agora/ tests/unit/test_message.py tests/unit/test_codec.py
git commit -m "feat: add message protocol layer with Message dataclass and JSON codec"
```

---

### Task 3: Capability Declaration

**Files:**
- Create: `agora/agent/capability.py`
- Create: `agora/agent/__init__.py`
- Test: `tests/unit/test_capability.py`

- [ ] **Step 3.1: Write failing test for Capability**

Create `tests/unit/test_capability.py`:

```python
import pytest
from agora.agent.capability import Capability, CapabilityRegistry


class TestCapability:
    def test_capability_creation(self):
        cap = Capability(
            name="math.add",
            description="Add two numbers",
            input_schema={"type": "object", "properties": {"a": {"type": "number"}}},
            output_schema={"type": "object", "properties": {"result": {"type": "number"}}}
        )
        assert cap.name == "math.add"
        assert cap.description == "Add two numbers"

    def test_capability_matches_exact(self):
        cap = Capability(name="math.add", description="Add")
        assert cap.matches("math.add") is True
        assert cap.matches("math.subtract") is False

    def test_capability_matches_wildcard(self):
        cap = Capability(name="math.add", description="Add")
        assert cap.matches("math.*") is True
        assert cap.matches("*.add") is True
        assert cap.matches("*") is True
        assert cap.matches("calc.*") is False


class TestCapabilityRegistry:
    def test_add_capability(self):
        reg = CapabilityRegistry()
        cap = Capability(name="math.add", description="Add")
        reg.add(cap)
        assert len(reg.list_all()) == 1

    def test_find_by_pattern(self):
        reg = CapabilityRegistry()
        reg.add(Capability(name="math.add", description="Add"))
        reg.add(Capability(name="math.multiply", description="Multiply"))
        reg.add(Capability(name="string.concat", description="Concat"))
        
        matches = reg.find("math.*")
        assert len(matches) == 2
        assert all(m.name.startswith("math.") for m in matches)

    def test_find_by_exact(self):
        reg = CapabilityRegistry()
        reg.add(Capability(name="math.add", description="Add"))
        
        matches = reg.find("math.add")
        assert len(matches) == 1
        assert matches[0].name == "math.add"
```

- [ ] **Step 3.2: Run test to verify it fails**

```bash
pytest tests/unit/test_capability.py -v
```

Expected: ImportError for agora.agent.capability

- [ ] **Step 3.3: Implement Capability and CapabilityRegistry**

Create `agora/agent/capability.py`:

```python
"""Capability declaration and matching."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Capability:
    """An Agent capability declaration.
    
    Attributes:
        name: Dot-separated identifier (e.g., "math.add")
        description: Human-readable description
        input_schema: JSON Schema for input validation
        output_schema: JSON Schema for output validation
    """
    name: str
    description: str
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None

    def matches(self, pattern: str) -> bool:
        """Check if capability matches a pattern.
        
        Supports wildcards:
        - "math.*" matches "math.add", "math.subtract"
        - "*.add" matches "math.add", "calc.add"
        - "*" matches everything
        """
        return fnmatch.fnmatch(self.name, pattern)


class CapabilityRegistry:
    """Registry for managing multiple capabilities."""
    
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
    
    def add(self, capability: Capability) -> None:
        """Add a capability to the registry."""
        self._capabilities[capability.name] = capability
    
    def get(self, name: str) -> Capability | None:
        """Get capability by exact name."""
        return self._capabilities.get(name)
    
    def find(self, pattern: str) -> list[Capability]:
        """Find capabilities matching pattern."""
        return [cap for cap in self._capabilities.values() if cap.matches(pattern)]
    
    def list_all(self) -> list[Capability]:
        """List all registered capabilities."""
        return list(self._capabilities.values())
    
    def remove(self, name: str) -> None:
        """Remove a capability by name."""
        self._capabilities.pop(name, None)
```

- [ ] **Step 3.4: Run tests to verify they pass**

```bash
pytest tests/unit/test_capability.py -v
```

Expected: 6 tests PASSED

- [ ] **Step 3.5: Commit**

```bash
git add agora/agent/capability.py tests/unit/test_capability.py
git commit -m "feat: add capability declaration and pattern matching"
```

---

### Task 4: MQTT Transport Layer

**Files:**
- Create: `agora/protocol/transport.py`
- Create: `tests/unit/test_transport.py`

- [ ] **Step 4.1: Write failing test for MqttTransport**

Create `tests/unit/test_transport.py`:

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from agora.protocol.transport import MqttTransport
from agora.protocol.message import Message


class TestMqttTransport:
    @pytest.mark.asyncio
    async def test_connect(self):
        with patch('aiomqtt.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            
            transport = MqttTransport(host="localhost", port=1883)
            await transport.connect()
            
            assert transport.is_connected is True

    @pytest.mark.asyncio
    async def test_subscribe(self):
        with patch('aiomqtt.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            
            transport = MqttTransport(host="localhost", port=1883)
            await transport.connect()
            await transport.subscribe("agora/agent/test/inbox")
            
            mock_instance.subscribe.assert_called_once_with("agora/agent/test/inbox")

    @pytest.mark.asyncio
    async def test_publish(self):
        with patch('aiomqtt.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            
            transport = MqttTransport(host="localhost", port=1883)
            await transport.connect()
            
            msg = Message(
                msg_id="test-id",
                from_agent="a",
                to_agent="b",
                capability="test",
                payload={"key": "value"}
            )
            await transport.publish("agora/agent/b/inbox", msg)
            
            mock_instance.publish.assert_called_once()
```

- [ ] **Step 4.2: Run test to verify it fails**

```bash
pytest tests/unit/test_transport.py -v
```

Expected: ImportError for agora.protocol.transport

- [ ] **Step 4.3: Implement MqttTransport**

Create `agora/protocol/transport.py`:

```python
"""MQTT transport layer abstraction."""
from __future__ import annotations

import asyncio
from typing import Callable

import aiomqtt
from agora.protocol.message import Message
from agora.protocol.codec import MessageCodec


class MqttTransport:
    """Async MQTT transport for Agent communication."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        keepalive: int = 60
    ) -> None:
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self._client: aiomqtt.Client | None = None
        self._message_handler: Callable[[Message], None] | None = None
        self._task: asyncio.Task | None = None
    
    @property
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        return self._client is not None
    
    async def connect(self) -> None:
        """Connect to MQTT broker."""
        self._client = aiomqtt.Client(
            hostname=self.host,
            port=self.port,
            keepalive=self.keepalive
        )
        await self._client.__aenter__()
    
    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
    
    async def subscribe(self, topic: str) -> None:
        """Subscribe to a topic."""
        if not self._client:
            raise RuntimeError("Not connected")
        await self._client.subscribe(topic)
    
    async def publish(self, topic: str, message: Message, qos: int = 1) -> None:
        """Publish a message to a topic."""
        if not self._client:
            raise RuntimeError("Not connected")
        payload = MessageCodec.encode(message)
        await self._client.publish(topic, payload=payload, qos=qos)
    
    def on_message(self, handler: Callable[[Message], None]) -> None:
        """Set message handler callback."""
        self._message_handler = handler
    
    async def start_message_loop(self) -> None:
        """Start receiving messages."""
        if not self._client:
            raise RuntimeError("Not connected")
        
        async for message in self._client.messages:
            if self._message_handler:
                try:
                    decoded = MessageCodec.decode(message.payload)
                    self._message_handler(decoded)
                except Exception as e:
                    print(f"Failed to decode message: {e}")
```

- [ ] **Step 4.4: Run tests to verify they pass**

```bash
pytest tests/unit/test_transport.py -v
```

Expected: 3 tests PASSED

- [ ] **Step 4.5: Commit**

```bash
git add agora/protocol/transport.py tests/unit/test_transport.py
git commit -m "feat: add MQTT transport layer with aiomqtt"
```

---

### Task 5: Hub In-Memory Registry

**Files:**
- Create: `hub/registry.py`
- Test: `tests/unit/test_hub_registry.py`

- [ ] **Step 5.1: Write failing test for AgentRegistry**

Create `tests/unit/test_hub_registry.py`:

```python
import pytest
from datetime import datetime
from hub.registry import AgentRegistry, AgentInfo


class TestAgentRegistry:
    def test_register_agent(self):
        reg = AgentRegistry()
        reg.register(
            agent_id="agent_1",
            api_key="key123",
            capabilities=["math.add"],
            endpoint="mqtt://hub:1883"
        )
        
        agent = reg.get("agent_1")
        assert agent is not None
        assert agent.agent_id == "agent_1"
        assert agent.capabilities == ["math.add"]
    
    def test_find_by_capability(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add", "math.sub"], "mqtt://hub:1883")
        reg.register("agent_2", "key2", ["math.multiply"], "mqtt://hub:1883")
        reg.register("agent_3", "key3", ["string.concat"], "mqtt://hub:1883")
        
        matches = reg.find_by_capability("math.*")
        assert len(matches) == 2
        assert all("math" in cap for agent in matches for cap in agent.capabilities)
    
    def test_unregister_agent(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add"], "mqtt://hub:1883")
        reg.unregister("agent_1")
        
        assert reg.get("agent_1") is None
    
    def test_update_heartbeat(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add"], "mqtt://hub:1883")
        
        old_time = reg.get("agent_1").last_heartbeat
        reg.update_heartbeat("agent_1")
        
        new_time = reg.get("agent_1").last_heartbeat
        assert new_time > old_time
    
    def test_get_stale_agents(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add"], "mqtt://hub:1883")
        # Simulate old heartbeat
        reg._agents["agent_1"].last_heartbeat = datetime.utcnow().timestamp() - 120
        
        stale = reg.get_stale_agents(timeout_seconds=60)
        assert len(stale) == 1
        assert stale[0] == "agent_1"
```

- [ ] **Step 5.2: Run test to verify it fails**

```bash
pytest tests/unit/test_hub_registry.py -v
```

Expected: ImportError for hub.registry

- [ ] **Step 5.3: Implement AgentRegistry**

Create `hub/registry.py`:

```python
"""Hub-side in-memory Agent registry."""
from __future__ import annotations

import fnmatch
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentInfo:
    """Information about a registered Agent."""
    agent_id: str
    api_key: str
    capabilities: list[str]
    endpoint: str
    last_heartbeat: float = field(default_factory=time.time)
    active_connections: int = 0
    messages_processed: int = 0
    
    def is_alive(self, timeout_seconds: float) -> bool:
        """Check if agent heartbeat is within timeout."""
        return (time.time() - self.last_heartbeat) < timeout_seconds


class AgentRegistry:
    """In-memory registry for managing Agent registrations."""
    
    def __init__(self) -> None:
        self._agents: dict[str, AgentInfo] = {}
    
    def register(
        self,
        agent_id: str,
        api_key: str,
        capabilities: list[str],
        endpoint: str
    ) -> AgentInfo:
        """Register a new agent or update existing."""
        agent = AgentInfo(
            agent_id=agent_id,
            api_key=api_key,
            capabilities=capabilities,
            endpoint=endpoint
        )
        self._agents[agent_id] = agent
        return agent
    
    def unregister(self, agent_id: str) -> None:
        """Remove an agent from registry."""
        self._agents.pop(agent_id, None)
    
    def get(self, agent_id: str) -> AgentInfo | None:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def update_heartbeat(self, agent_id: str) -> bool:
        """Update heartbeat timestamp for an agent."""
        if agent_id in self._agents:
            self._agents[agent_id].last_heartbeat = time.time()
            return True
        return False
    
    def increment_connections(self, agent_id: str) -> None:
        """Increment active connection count."""
        if agent_id in self._agents:
            self._agents[agent_id].active_connections += 1
    
    def decrement_connections(self, agent_id: str) -> None:
        """Decrement active connection count."""
        if agent_id in self._agents:
            self._agents[agent_id].active_connections = max(
                0, self._agents[agent_id].active_connections - 1
            )
    
    def find_by_capability(self, pattern: str) -> list[AgentInfo]:
        """Find agents with capabilities matching pattern."""
        return [
            agent for agent in self._agents.values()
            if any(fnmatch.fnmatch(cap, pattern) for cap in agent.capabilities)
        ]
    
    def get_stale_agents(self, timeout_seconds: float) -> list[str]:
        """Get list of agent IDs that haven't sent heartbeat."""
        return [
            agent_id for agent_id, agent in self._agents.items()
            if not agent.is_alive(timeout_seconds)
        ]
    
    def list_all(self) -> list[AgentInfo]:
        """List all registered agents."""
        return list(self._agents.values())
```

- [ ] **Step 5.4: Run tests to verify they pass**

```bash
pytest tests/unit/test_hub_registry.py -v
```

Expected: 6 tests PASSED

- [ ] **Step 5.5: Commit**

```bash
git add hub/registry.py tests/unit/test_hub_registry.py
git commit -m "feat: add hub in-memory agent registry with heartbeat tracking"
```

---

### Task 6: Load Balancer

**Files:**
- Create: `agora/routing/load_balance.py`
- Test: `tests/unit/test_load_balance.py`

- [ ] **Step 6.1: Write failing test for LeastConnectionsStrategy**

Create `tests/unit/test_load_balance.py`:

```python
import pytest
from agora.routing.load_balance import LeastConnectionsStrategy
from hub.registry import AgentInfo


class TestLeastConnectionsStrategy:
    def test_select_single_agent(self):
        strategy = LeastConnectionsStrategy()
        agents = [
            AgentInfo("agent_1", "key1", ["math.add"], "mqtt://hub:1883", active_connections=5)
        ]
        
        selected = strategy.select(agents)
        assert selected == "agent_1"
    
    def test_select_least_connections(self):
        strategy = LeastConnectionsStrategy()
        agents = [
            AgentInfo("agent_1", "key1", ["math.add"], "mqtt://hub:1883", active_connections=5),
            AgentInfo("agent_2", "key2", ["math.add"], "mqtt://hub:1883", active_connections=2),
            AgentInfo("agent_3", "key3", ["math.add"], "mqtt://hub:1883", active_connections=8),
        ]
        
        selected = strategy.select(agents)
        assert selected == "agent_2"
    
    def test_select_empty_list(self):
        strategy = LeastConnectionsStrategy()
        selected = strategy.select([])
        assert selected is None
    
    def test_select_tie_break(self):
        strategy = LeastConnectionsStrategy()
        agents = [
            AgentInfo("agent_1", "key1", ["math.add"], "mqtt://hub:1883", active_connections=2),
            AgentInfo("agent_2", "key2", ["math.add"], "mqtt://hub:1883", active_connections=2),
        ]
        
        selected = strategy.select(agents)
        assert selected in ["agent_1", "agent_2"]
```

- [ ] **Step 6.2: Run test to verify it fails**

```bash
pytest tests/unit/test_load_balance.py -v
```

Expected: ImportError for agora.routing.load_balance

- [ ] **Step 6.3: Implement LeastConnectionsStrategy**

Create `agora/routing/load_balance.py`:

```python
"""Load balancing strategies for Agent routing."""
from __future__ import annotations

import random
from typing import Protocol

from hub.registry import AgentInfo


class LoadBalanceStrategy(Protocol):
    """Protocol for load balancing strategies."""
    
    def select(self, agents: list[AgentInfo]) -> str | None:
        """Select an agent from the list. Returns agent_id or None."""
        ...


class LeastConnectionsStrategy:
    """Select agent with fewest active connections."""
    
    def select(self, agents: list[AgentInfo]) -> str | None:
        if not agents:
            return None
        
        min_connections = min(a.active_connections for a in agents)
        candidates = [a for a in agents if a.active_connections == min_connections]
        
        # Random tie-break
        return random.choice(candidates).agent_id


class RoundRobinStrategy:
    """Round-robin selection."""
    
    def __init__(self) -> None:
        self._index = 0
    
    def select(self, agents: list[AgentInfo]) -> str | None:
        if not agents:
            return None
        
        agent_id = agents[self._index % len(agents)].agent_id
        self._index += 1
        return agent_id


class RandomStrategy:
    """Random selection."""
    
    def select(self, agents: list[AgentInfo]) -> str | None:
        if not agents:
            return None
        return random.choice(agents).agent_id
```

- [ ] **Step 6.4: Run tests to verify they pass**

```bash
pytest tests/unit/test_load_balance.py -v
```

Expected: 4 tests PASSED

- [ ] **Step 6.5: Commit**

```bash
git add agora/routing/load_balance.py tests/unit/test_load_balance.py
git commit -m "feat: add load balancing strategies (least-connections, round-robin, random)"
```

---

### Task 7: Hub Message Queue Manager

**Files:**
- Create: `hub/queue.py`
- Test: `tests/unit/test_hub_queue.py`

- [ ] **Step 7.1: Write failing test for MessageQueueManager**

Create `tests/unit/test_hub_queue.py`:

```python
import pytest
from datetime import datetime, timedelta
from agora.protocol.message import Message
from hub.queue import MessageQueueManager, QueuedMessage


class TestMessageQueueManager:
    def test_enqueue_message(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )
        
        mgr.enqueue("agent_b", msg)
        assert mgr.queue_size("agent_b") == 1
    
    def test_dequeue_message(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={"key": "value"}
        )
        
        mgr.enqueue("agent_b", msg)
        queued = mgr.dequeue("agent_b")
        
        assert queued is not None
        assert queued.msg_id == "test-1"
        assert mgr.queue_size("agent_b") == 0
    
    def test_dequeue_empty(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        queued = mgr.dequeue("nonexistent")
        assert queued is None
    
    def test_cleanup_expired(self):
        mgr = MessageQueueManager(ttl_seconds=1)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )
        
        mgr.enqueue("agent_b", msg)
        # Simulate time passing
        for qm in mgr._queues["agent_b"]:
            qm.timestamp = datetime.utcnow() - timedelta(seconds=2)
        
        mgr.cleanup_expired()
        assert mgr.queue_size("agent_b") == 0
    
    def test_clear_queue(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )
        
        mgr.enqueue("agent_b", msg)
        mgr.clear_queue("agent_b")
        assert mgr.queue_size("agent_b") == 0
```

- [ ] **Step 7.2: Run test to verify it fails**

```bash
pytest tests/unit/test_hub_queue.py -v
```

Expected: ImportError for hub.queue

- [ ] **Step 7.3: Implement MessageQueueManager**

Create `hub/queue.py`:

```python
"""Hub message queue management with TTL."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from agora.protocol.message import Message


@dataclass
class QueuedMessage:
    """A message in the queue with metadata."""
    msg_id: str
    from_agent: str
    to_agent: str
    capability: str
    payload: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_message(cls, msg: Message) -> QueuedMessage:
        return cls(
            msg_id=msg.msg_id,
            from_agent=msg.from_agent,
            to_agent=msg.to_agent,
            capability=msg.capability,
            payload=msg.payload
        )


class MessageQueueManager:
    """Manages per-Agent message queues with TTL."""
    
    def __init__(self, ttl_seconds: float = 300, max_size: int = 1000) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._queues: dict[str, deque[QueuedMessage]] = {}
    
    def enqueue(self, agent_id: str, message: Message) -> bool:
        """Add message to agent's queue. Returns False if queue full."""
        if agent_id not in self._queues:
            self._queues[agent_id] = deque()
        
        if len(self._queues[agent_id]) >= self.max_size:
            return False
        
        queued = QueuedMessage.from_message(message)
        self._queues[agent_id].append(queued)
        return True
    
    def dequeue(self, agent_id: str) -> QueuedMessage | None:
        """Get next message for agent. Returns None if empty."""
        if agent_id not in self._queues:
            return None
        
        queue = self._queues[agent_id]
        while queue:
            msg = queue.popleft()
            # Check if expired
            age = (datetime.utcnow() - msg.timestamp).total_seconds()
            if age <= self.ttl_seconds:
                return msg
        
        return None
    
    def queue_size(self, agent_id: str) -> int:
        """Get current queue size for agent."""
        return len(self._queues.get(agent_id, []))
    
    def clear_queue(self, agent_id: str) -> None:
        """Clear all messages for an agent."""
        self._queues.pop(agent_id, None)
    
    def cleanup_expired(self) -> int:
        """Remove expired messages from all queues. Returns count removed."""
        removed = 0
        cutoff = datetime.utcnow() - timedelta(seconds=self.ttl_seconds)
        
        for agent_id, queue in self._queues.items():
            original_len = len(queue)
            # Filter out expired messages
            self._queues[agent_id] = deque(
                msg for msg in queue if msg.timestamp > cutoff
            )
            removed += original_len - len(self._queues[agent_id])
        
        return removed
```

- [ ] **Step 7.4: Run tests to verify they pass**

```bash
pytest tests/unit/test_hub_queue.py -v
```

Expected: 5 tests PASSED

- [ ] **Step 7.5: Commit**

```bash
git add hub/queue.py tests/unit/test_hub_queue.py
git commit -m "feat: add hub message queue manager with TTL expiration"
```

---

### Task 8: Hub Main Service

**Files:**
- Create: `hub/main.py`
- Create: `hub/config.yaml`
- Create: `hub/Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 8.1: Create Hub config file**

Create `hub/config.yaml`:

```yaml
hub:
  mqtt:
    host: "0.0.0.0"
    port: 1883
    ws_port: 8083
    max_connections: 10000
    
  auth:
    type: token
    tokens_file: ./tokens.json
    
  queue:
    ttl_seconds: 300
    max_size_per_agent: 1000
    cleanup_interval: 60
    
  heartbeat:
    interval_seconds: 30
    timeout_seconds: 60
    check_interval: 10
    
  logging:
    level: INFO
```

- [ ] **Step 8.2: Create Hub main service**

Create `hub/main.py`:

```python
#!/usr/bin/env python3
"""Agora Hub - Central coordination service."""
from __future__ import annotations

import asyncio
import json
import signal
import sys
from pathlib import Path

import aiomqtt
import yaml
from agora.protocol.message import Message
from agora.protocol.codec import MessageCodec
from agora.routing.load_balance import LeastConnectionsStrategy
from hub.registry import AgentRegistry
from hub.queue import MessageQueueManager


class AgoraHub:
    """Main Hub service coordinating Agent communication."""
    
    def __init__(self, config_path: str = "hub/config.yaml") -> None:
        with open(config_path) as f:
            self.config = yaml.safe_load(f)["hub"]
        
        self.registry = AgentRegistry()
        self.queue_manager = MessageQueueManager(
            ttl_seconds=self.config["queue"]["ttl_seconds"],
            max_size=self.config["queue"]["max_size_per_agent"]
        )
        self.load_balancer = LeastConnectionsStrategy()
        self._shutdown_event = asyncio.Event()
        self._tasks: list[asyncio.Task] = []
    
    async def run(self) -> None:
        """Run the Hub service."""
        print(f"Starting Agora Hub on {self.config['mqtt']['host']}:{self.config['mqtt']['port']}")
        
        # Start background tasks
        self._tasks.append(asyncio.create_task(self._cleanup_loop()))
        self._tasks.append(asyncio.create_task(self._heartbeat_check_loop()))
        
        async with aiomqtt.Client(
            hostname=self.config["mqtt"]["host"],
            port=self.config["mqtt"]["port"]
        ) as client:
            # Subscribe to Hub topics
            await client.subscribe("agora/hub/registry")
            await client.subscribe("agora/hub/heartbeat")
            await client.subscribe("agora/hub/discover")
            
            print("Hub ready. Waiting for messages...")
            
            async for message in client.messages:
                if self._shutdown_event.is_set():
                    break
                await self._handle_message(client, message)
    
    async def _handle_message(self, client: aiomqtt.Client, message: aiomqtt.Message) -> None:
        """Handle incoming MQTT message."""
        topic = str(message.topic)
        
        try:
            payload = json.loads(message.payload.decode())
        except json.JSONDecodeError:
            print(f"Invalid JSON on {topic}")
            return
        
        if "registry" in topic:
            await self._handle_registry(client, payload)
        elif "heartbeat" in topic:
            await self._handle_heartbeat(payload)
        elif "discover" in topic:
            await self._handle_discover(client, payload)
    
    async def _handle_registry(self, client: aiomqtt.Client, payload: dict) -> None:
        """Handle agent registration."""
        msg_type = payload.get("type")
        agent_id = payload.get("agent_id")
        
        if msg_type == "register":
            self.registry.register(
                agent_id=agent_id,
                api_key=payload.get("api_key"),
                capabilities=payload.get("capabilities", []),
                endpoint=payload.get("endpoint", "")
            )
            print(f"Agent registered: {agent_id}")
            
            # Broadcast online event
            await client.publish(
                "agora/hub/events",
                json.dumps({"type": "agent_online", "agent_id": agent_id}).encode()
            )
            
        elif msg_type == "unregister":
            self.registry.unregister(agent_id)
            self.queue_manager.clear_queue(agent_id)
            print(f"Agent unregistered: {agent_id}")
            
            await client.publish(
                "agora/hub/events",
                json.dumps({"type": "agent_offline", "agent_id": agent_id}).encode()
            )
    
    async def _handle_heartbeat(self, payload: dict) -> None:
        """Handle agent heartbeat."""
        agent_id = payload.get("agent_id")
        if self.registry.update_heartbeat(agent_id):
            print(f"Heartbeat from: {agent_id}")
    
    async def _handle_discover(self, client: aiomqtt.Client, payload: dict) -> None:
        """Handle capability discovery request."""
        capability = payload.get("capability")
        requester = payload.get("agent_id")
        
        matches = self.registry.find_by_capability(capability)
        if matches:
            # Select using load balancer
            selected_id = self.load_balancer.select(matches)
            if selected_id:
                self.registry.increment_connections(selected_id)
                
                # Send response
                response = {
                    "type": "discovery_response",
                    "capability": capability,
                    "agents": [{"id": selected_id}]
                }
                await client.publish(
                    f"agora/agent/{requester}/inbox",
                    json.dumps(response).encode()
                )
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired messages."""
        while not self._shutdown_event.is_set():
            await asyncio.sleep(self.config["queue"]["cleanup_interval"])
            removed = self.queue_manager.cleanup_expired()
            if removed > 0:
                print(f"Cleaned up {removed} expired messages")
    
    async def _heartbeat_check_loop(self) -> None:
        """Check for stale agents."""
        while not self._shutdown_event.is_set():
            await asyncio.sleep(self.config["heartbeat"]["check_interval"])
            stale = self.registry.get_stale_agents(
                self.config["heartbeat"]["timeout_seconds"]
            )
            for agent_id in stale:
                print(f"Agent timeout: {agent_id}")
                self.registry.unregister(agent_id)
                self.queue_manager.clear_queue(agent_id)
    
    def shutdown(self) -> None:
        """Signal shutdown."""
        print("Shutting down...")
        self._shutdown_event.set()
        for task in self._tasks:
            task.cancel()


def main():
    hub = AgoraHub()
    
    def signal_handler(sig, frame):
        hub.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    asyncio.run(hub.run())


if __name__ == "__main__":
    main()
```

- [ ] **Step 8.3: Create Hub Dockerfile**

Create `hub/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install -e "."

# Copy hub code
COPY hub/ ./hub/
COPY agora/ ./agora/

# Expose MQTT ports
EXPOSE 1883 8083

CMD ["python", "hub/main.py"]
```

- [ ] **Step 8.4: Create docker-compose.yml**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  hub:
    build:
      context: .
      dockerfile: hub/Dockerfile
    ports:
      - "1883:1883"
      - "8083:8083"
    volumes:
      - ./hub/config.yaml:/app/hub/config.yaml
      - ./tokens.json:/app/tokens.json
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - agora-network

networks:
  agora-network:
    driver: bridge
```

- [ ] **Step 8.5: Commit**

```bash
git add hub/main.py hub/config.yaml hub/Dockerfile docker-compose.yml
git commit -m "feat: add hub main service with MQTT broker integration"
```

---

### Task 9: Agent Base Class

**Files:**
- Create: `agora/agent/base.py`
- Create: `agora/agent/context.py`
- Create: `agora/discovery/registry.py`
- Create: `agora/discovery/resolver.py`

- [ ] **Step 9.1: Create Agent context**

Create `agora/agent/context.py`:

```python
"""Agent runtime context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agora.agent.capability import CapabilityRegistry


@dataclass
class AgentContext:
    """Runtime context for an Agent."""
    agent_id: str
    hub_host: str = "localhost"
    hub_port: int = 1883
    capabilities: CapabilityRegistry = field(default_factory=CapabilityRegistry)
    state: dict[str, Any] = field(default_factory=dict)
```

- [ ] **Step 9.2: Create Agent discovery registry client**

Create `agora/discovery/registry.py`:

```python
"""Client-side Agent registration."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agora.protocol.transport import MqttTransport


class AgentRegistryClient:
    """Client for registering with Hub."""
    
    def __init__(self, transport: MqttTransport, agent_id: str, api_key: str) -> None:
        self.transport = transport
        self.agent_id = agent_id
        self.api_key = api_key
    
    async def register(self, capabilities: list[str], endpoint: str) -> None:
        """Register with Hub."""
        message = {
            "type": "register",
            "agent_id": self.agent_id,
            "api_key": self.api_key,
            "capabilities": capabilities,
            "endpoint": endpoint
        }
        await self.transport.publish(
            "agora/hub/registry",
            message
        )
    
    async def unregister(self) -> None:
        """Unregister from Hub."""
        message = {
            "type": "unregister",
            "agent_id": self.agent_id
        }
        await self.transport.publish(
            "agora/hub/registry",
            message
        )
    
    async def send_heartbeat(self) -> None:
        """Send heartbeat to Hub."""
        message = {
            "agent_id": self.agent_id,
            "timestamp": json.dumps({})  # Placeholder
        }
        await self.transport.publish(
            "agora/hub/heartbeat",
            message
        )
```

- [ ] **Step 9.3: Create Agent discovery resolver**

Create `agora/discovery/resolver.py`:

```python
"""Client-side capability discovery."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agora.protocol.transport import MqttTransport


class CapabilityResolver:
    """Client for discovering capabilities."""
    
    def __init__(self, transport: MqttTransport, agent_id: str) -> None:
        self.transport = transport
        self.agent_id = agent_id
        self._pending_responses: dict[str, asyncio.Future] = {}
    
    async def discover(self, capability: str) -> list[dict]:
        """Discover agents with given capability."""
        message = {
            "agent_id": self.agent_id,
            "capability": capability
        }
        
        future = asyncio.get_event_loop().create_future()
        self._pending_responses[capability] = future
        
        await self.transport.publish(
            "agora/hub/discover",
            message
        )
        
        try:
            response = await asyncio.wait_for(future, timeout=5.0)
            return response.get("agents", [])
        except asyncio.TimeoutError:
            return []
    
    def handle_response(self, response: dict) -> None:
        """Handle discovery response."""
        capability = response.get("capability")
        if capability in self._pending_responses:
            future = self._pending_responses.pop(capability)
            if not future.done():
                future.set_result(response)
```

- [ ] **Step 9.4: Implement AgentBase**

Create `agora/agent/base.py`:

```python
"""Base Agent class."""
from __future__ import annotations

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any

import yaml
from agora.protocol.message import Message
from agora.protocol.transport import MqttTransport
from agora.agent.context import AgentContext
from agora.agent.capability import Capability, CapabilityRegistry
from agora.discovery.registry import AgentRegistryClient
from agora.discovery.resolver import CapabilityResolver


class AgentBase(ABC):
    """Base class for all Agents."""
    
    def __init__(
        self,
        manifest_path: str,
        hub_host: str = "localhost",
        hub_port: int = 1883
    ) -> None:
        self.manifest = self._load_manifest(manifest_path)
        self.context = AgentContext(
            agent_id=self.manifest["agent"]["id"],
            hub_host=hub_host,
            hub_port=hub_port,
            capabilities=self._load_capabilities()
        )
        self.transport = MqttTransport(host=hub_host, port=hub_port)
        self.registry_client = AgentRegistryClient(
            self.transport,
            self.context.agent_id,
            self.manifest["agent"]["api_key"]
        )
        self.resolver = CapabilityResolver(self.transport, self.context.agent_id)
        self._running = False
        self._heartbeat_task: asyncio.Task | None = None
    
    def _load_manifest(self, path: str) -> dict:
        """Load agent manifest from YAML."""
        with open(path) as f:
            return yaml.safe_load(f)
    
    def _load_capabilities(self) -> CapabilityRegistry:
        """Load capabilities from manifest."""
        registry = CapabilityRegistry()
        for cap_data in self.manifest.get("capabilities", []):
            cap = Capability(
                name=cap_data["name"],
                description=cap_data.get("description", ""),
                input_schema=cap_data.get("input_schema"),
                output_schema=cap_data.get("output_schema")
            )
            registry.add(cap)
        return registry
    
    async def start(self) -> None:
        """Start the agent."""
        await self.transport.connect()
        
        # Subscribe to inbox
        inbox_topic = f"agora/agent/{self.context.agent_id}/inbox"
        await self.transport.subscribe(inbox_topic)
        self.transport.on_message(self._on_message)
        
        # Register with Hub
        capabilities = [c.name for c in self.context.capabilities.list_all()]
        await self.registry_client.register(
            capabilities=capabilities,
            endpoint=f"mqtt://{self.context.hub_host}:{self.context.hub_port}"
        )
        
        # Start heartbeat
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Start message loop
        await self.transport.start_message_loop()
    
    async def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        await self.registry_client.unregister()
        await self.transport.disconnect()
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats."""
        while self._running:
            try:
                await self.registry_client.send_heartbeat()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    def _on_message(self, message: Message) -> None:
        """Handle incoming message."""
        asyncio.create_task(self._process_message(message))
    
    async def _process_message(self, message: Message) -> None:
        """Process and respond to message."""
        response = await self.handle_message(message)
        if response:
            await self.transport.publish(
                f"agora/agent/{message.from_agent}/inbox",
                response
            )
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Message | None:
        """Handle a message. Override in subclass."""
        pass
    
    async def send_to_capability(
        self,
        capability: str,
        payload: dict[str, Any]
    ) -> None:
        """Send message to agents with given capability."""
        # Discover agents
        agents = await self.resolver.discover(capability)
        if not agents:
            print(f"No agents found for capability: {capability}")
            return
        
        target = agents[0]["id"]
        message = Message(
            msg_id=str(uuid.uuid4()),
            from_agent=self.context.agent_id,
            to_agent=target,
            capability=capability,
            payload=payload
        )
        
        await self.transport.publish(
            f"agora/agent/{target}/inbox",
            message
        )
```

- [ ] **Step 9.5: Commit**

```bash
git add agora/agent/base.py agora/agent/context.py agora/discovery/
git commit -m "feat: add Agent base class with registration and discovery"
```

---

### Task 10: Echo Agent Example

**Files:**
- Create: `agents/__init__.py`
- Create: `agents/echo_agent/__init__.py`
- Create: `agents/echo_agent/agent.py`
- Create: `agents/echo_agent/manifest.yaml`

- [ ] **Step 10.1: Create Echo Agent**

Create `agents/echo_agent/agent.py`:

```python
#!/usr/bin/env python3
"""Echo Agent - for testing."""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from agora.agent.base import AgentBase
from agora.protocol.message import Message


class EchoAgent(AgentBase):
    """Echo agent that returns received messages."""
    
    async def handle_message(self, message: Message) -> Message | None:
        """Echo the message back."""
        print(f"Received: {message.payload}")
        
        return Message(
            msg_id=str(uuid.uuid4()),
            from_agent=self.context.agent_id,
            to_agent=message.from_agent,
            capability="echo.response",
            payload={
                "echo": message.payload,
                "received_at": datetime.utcnow().isoformat()
            }
        )


async def main():
    manifest_path = Path(__file__).parent / "manifest.yaml"
    agent = EchoAgent(str(manifest_path))
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 10.2: Create Echo Agent manifest**

Create `agents/echo_agent/manifest.yaml`:

```yaml
agent:
  id: echo_agent
  version: "1.0.0"
  description: "Echo agent for testing"
  api_key: ${ECHO_AGENT_API_KEY:-echo_key_123}

capabilities:
  - name: echo.send
    description: "Send a message to be echoed back"
    input_schema:
      type: object
      properties:
        message:
          type: string
    output_schema:
      type: object
      properties:
        echo:
          type: object
        received_at:
          type: string
```

- [ ] **Step 10.3: Commit**

```bash
git add agents/
git commit -m "feat: add echo agent example"
```

---

### Task 11: Calculator Agent Example

**Files:**
- Create: `agents/calculator_agent/agent.py`
- Create: `agents/calculator_agent/manifest.yaml`

- [ ] **Step 11.1: Create Calculator Agent**

Create `agents/calculator_agent/agent.py`:

```python
#!/usr/bin/env python3
"""Calculator Agent - performs math operations."""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from agora.agent.base import AgentBase
from agora.protocol.message import Message


class CalculatorAgent(AgentBase):
    """Calculator agent for math operations."""
    
    async def handle_message(self, message: Message) -> Message | None:
        """Handle math operations."""
        cap = message.capability
        payload = message.payload
        
        if cap == "math.add":
            result = payload["a"] + payload["b"]
        elif cap == "math.subtract":
            result = payload["a"] - payload["b"]
        elif cap == "math.multiply":
            result = payload["a"] * payload["b"]
        elif cap == "math.divide":
            if payload["b"] == 0:
                result = {"error": "Division by zero"}
            else:
                result = payload["a"] / payload["b"]
        else:
            return None
        
        return Message(
            msg_id=str(uuid.uuid4()),
            from_agent=self.context.agent_id,
            to_agent=message.from_agent,
            capability=f"{cap}.response",
            payload={"result": result}
        )


async def main():
    manifest_path = Path(__file__).parent / "manifest.yaml"
    agent = CalculatorAgent(str(manifest_path))
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 11.2: Create Calculator manifest**

Create `agents/calculator_agent/manifest.yaml`:

```yaml
agent:
  id: calculator_agent
  version: "1.0.0"
  description: "Math calculator agent"
  api_key: ${CALC_AGENT_API_KEY:-calc_key_123}

capabilities:
  - name: math.add
    description: "Add two numbers"
    input_schema:
      type: object
      required: ["a", "b"]
      properties:
        a: { type: number }
        b: { type: number }
    output_schema:
      type: object
      properties:
        result: { type: number }

  - name: math.subtract
    description: "Subtract two numbers"
    input_schema:
      type: object
      required: ["a", "b"]
      properties:
        a: { type: number }
        b: { type: number }

  - name: math.multiply
    description: "Multiply two numbers"
    input_schema:
      type: object
      required: ["a", "b"]
      properties:
        a: { type: number }
        b: { type: number }

  - name: math.divide
    description: "Divide two numbers"
    input_schema:
      type: object
      required: ["a", "b"]
      properties:
        a: { type: number }
        b: { type: number }
```

- [ ] **Step 11.3: Commit**

```bash
git add agents/calculator_agent/
git commit -m "feat: add calculator agent example with 4 math operations"
```

---

### Task 12: Integration Tests

**Files:**
- Create: `tests/integration/test_agent_lifecycle.py`
- Create: `tests/integration/test_message_routing.py`

- [ ] **Step 12.1: Create agent lifecycle test**

Create `tests/integration/test_agent_lifecycle.py`:

```python
import pytest
import asyncio
from agora.protocol.message import Message


@pytest.mark.asyncio
async def test_agent_registration_flow():
    """Test agent can register and unregister."""
    # This test requires running Hub
    # Skip if Hub not available
    pytest.skip("Requires running Hub - run manually")


@pytest.mark.asyncio
async def test_message_echo():
    """Test echo agent responds correctly."""
    pytest.skip("Requires running Hub and Echo Agent - run manually")
```

- [ ] **Step 12.2: Create message routing test**

Create `tests/integration/test_message_routing.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_capability_routing():
    """Test messages route to correct capability."""
    pytest.skip("Requires running Hub - run manually")
```

- [ ] **Step 12.3: Commit**

```bash
git add tests/integration/
git commit -m "test: add integration test placeholders"
```

---

### Task 13: Example Scripts

**Files:**
- Create: `examples/basic_discovery.py`
- Create: `examples/multi_agent_chat.py`

- [ ] **Step 13.1: Create basic discovery example**

Create `examples/basic_discovery.py`:

```python
#!/usr/bin/env python3
"""Basic discovery example - find agents with capabilities."""
import asyncio
from agora.protocol.transport import MqttTransport
from agora.discovery.resolver import CapabilityResolver


async def main():
    transport = MqttTransport("localhost", 1883)
    await transport.connect()
    
    resolver = CapabilityResolver(transport, "test_client")
    
    print("Discovering math agents...")
    agents = await resolver.discover("math.*")
    
    print(f"Found {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent['id']}")
    
    await transport.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 13.2: Create multi-agent chat example**

Create `examples/multi_agent_chat.py`:

```python
#!/usr/bin/env python3
"""Multi-agent chat example."""
import asyncio
import uuid
from agora.protocol.transport import MqttTransport
from agora.protocol.message import Message


async def main():
    transport = MqttTransport("localhost", 1883)
    await transport.connect()
    
    # Send message to echo agent
    msg = Message(
        msg_id=str(uuid.uuid4()),
        from_agent="chat_client",
        to_agent="echo_agent",
        capability="echo.send",
        payload={"message": "Hello from chat!"}
    )
    
    await transport.publish("agora/agent/echo_agent/inbox", msg)
    print("Message sent to echo agent")
    
    await asyncio.sleep(1)
    await transport.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 13.3: Commit**

```bash
git add examples/
git commit -m "feat: add example scripts for discovery and multi-agent chat"
```

---

### Task 14: Documentation

**Files:**
- Create: `docs/architecture.md`
- Create: `docs/quickstart.md`
- Update: `README.md`

- [ ] **Step 14.1: Create architecture doc**

Create `docs/architecture.md`:

```markdown
# Agora Architecture

## Overview

Agora is a hub-based Agent coordination platform using MQTT for transport.

## Components

### Hub
- MQTT Broker integration
- In-memory Agent registry
- Message queue with TTL
- Heartbeat monitoring

### Agent SDK
- Base class for Agent development
- Capability declaration
- Message routing
- Discovery client

## Message Flow

1. Agent connects to Hub via MQTT
2. Agent registers with capabilities
3. Hub maintains registry and routes messages
4. Messages queued with TTL for offline agents
```

- [ ] **Step 14.2: Create quickstart doc**

Create `docs/quickstart.md`:

```markdown
# Quick Start

## 1. Start Hub

```bash
docker-compose up -d hub
```

## 2. Run Echo Agent

```bash
python -m agents.echo_agent.agent
```

## 3. Test with Example

```bash
python examples/multi_agent_chat.py
```

## Create Custom Agent

1. Create `manifest.yaml` with capabilities
2. Subclass `AgentBase`
3. Implement `handle_message()`
4. Run with `agent.start()`
```

- [ ] **Step 14.3: Update README**

Update `README.md` with full content.

- [ ] **Step 14.4: Commit**

```bash
git add docs/ README.md
git commit -m "docs: add architecture and quickstart documentation"
```

---

### Task 15: Final Integration

**Files:**
- Update: `pyproject.toml` (add scripts)
- Create: `tokens.json` (example)

- [ ] **Step 15.1: Add CLI scripts to pyproject.toml**

Add to `pyproject.toml`:

```toml
[project.scripts]
agora-hub = "hub.main:main"
echo-agent = "agents.echo_agent.agent:main"
calc-agent = "agents.calculator_agent.agent:main"
```

- [ ] **Step 15.2: Create example tokens file**

Create `tokens.json`:

```json
{
  "echo_agent": "echo_key_123",
  "calculator_agent": "calc_key_123"
}
```

- [ ] **Step 15.3: Final commit**

```bash
git add pyproject.toml tokens.json
git commit -m "chore: add CLI entry points and example tokens"
```

---

## Verification Steps

After completing all tasks:

```bash
# 1. Install
cd /Users/dr4/WorkSpace/context-infrastructure/adhoc_jobs/git/myAgent-Shopping/AgentHub
pip install -e ".[dev]"

# 2. Run tests
pytest tests/unit/ -v

# 3. Start Hub
docker-compose up -d hub

# 4. Run Echo Agent in terminal 1
python -m agents.echo_agent.agent

# 5. Run example in terminal 2
python examples/multi_agent_chat.py
```

## Self-Review Checklist

- [ ] All unit tests pass
- [ ] Hub starts without errors
- [ ] Agent can register
- [ ] Messages route correctly
- [ ] Example scripts work

