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
