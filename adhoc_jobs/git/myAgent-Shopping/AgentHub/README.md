# Agora

Agent registration, capability declaration and discovery platform.

## Features

- **Agent Registration**: Agents register with the Hub using MQTT
- **Capability Declaration**: Agents declare their capabilities using structured JSON
- **Service Discovery**: Discover agents by capability with pattern matching
- **Message Routing**: Hub routes messages to appropriate agents
- **Load Balancing**: Least-connections strategy for agent selection
- **TTL Message Queue**: Messages expire after timeout for offline agents

## Quick Start

### Install

```bash
pip install -e ".[dev]"
```

### Run Hub

```bash
docker-compose up hub
```

### Run Example Agent

```bash
python -m agents.echo_agent.agent
```

## Architecture

See [docs/agora/architecture.md](docs/agora/architecture.md) for detailed architecture.

## Documentation

- [Quick Start](docs/agora/quickstart.md)
- [Architecture](docs/agora/architecture.md)

## Project Structure

```
agora/
├── agora/              # Core SDK library
│   ├── protocol/       # Message protocol
│   ├── agent/          # Agent base class
│   ├── discovery/      # Registration & discovery
│   └── routing/        # Load balancing
├── hub/                # Central Hub service
├── agents/             # Example agents
├── examples/           # Usage examples
└── tests/              # Unit & integration tests
```
