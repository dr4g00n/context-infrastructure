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
