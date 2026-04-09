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
